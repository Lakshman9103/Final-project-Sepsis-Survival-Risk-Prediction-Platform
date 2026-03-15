import sys
import os
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path so we can import src
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Now import from src
from src.feature_engineering import engineer_features, get_feature_info
from src.model_utils import load_model, make_prediction, classify_mortality_risk, validate_features

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Sepsis Survival & Risk Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high { color: #d62728; font-weight: bold; }
    .risk-moderate { color: #ff7f0e; font-weight: bold; }
    .risk-low { color: #2ca02c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def get_model():
    """Load the sepsis prediction model."""
    import os
    
    # Get absolute path to this script
    current_script = os.path.abspath(__file__)
    app_dir = os.path.dirname(current_script)
    project_root = os.path.dirname(app_dir)
    model_path = os.path.join(project_root, "models", "sepsis_final_model.pkl")
    
    if not os.path.exists(model_path):
        # Try alternative: check if we're running from project root
        alt_path = os.path.join(os.getcwd(), "models", "sepsis_final_model.pkl")
        if os.path.exists(alt_path):
            model_path = alt_path
        else:
            raise FileNotFoundError(
                f"Model file not found!\n"
                f"Tried:\n"
                f"1. {model_path}\n"
                f"2. {alt_path}\n"
                f"Current working directory: {os.getcwd()}\n"
                f"Script location: {current_script}"
            )
    
    st.info(f"✅ Loading model from: {model_path}")
    return load_model(model_path)

# Preprocessing function
def preprocess_patient_input(age: int, sex: str, episode: int) -> pd.DataFrame:
    """
    Preprocess patient input using feature engineering pipeline.
    
    Args:
        age: Patient age in years
        sex: Biological sex (Male/Female)
        episode: Number of sepsis episodes
        
    Returns:
        DataFrame with engineered features ready for model prediction
    """
    # Create input dataframe
    data = {
        'age': [age],
        'sex': [sex.lower()],  # Ensure lowercase for mapping
        'episode': [episode],
        'outcome': [1]  # Dummy value, not used for prediction
    }
    df = pd.DataFrame(data)
    
    # Apply feature engineering pipeline
    df_engineered = engineer_features(df)
    
    # Remove outcome column if present (not needed for prediction)
    if 'outcome' in df_engineered.columns:
        df_engineered = df_engineered.drop('outcome', axis=1)
    
    return df_engineered

def generate_shap_explanation(model, features):
    """Generate SHAP force plot for model interpretability"""
    if not SHAP_AVAILABLE:
        return None
    
    try:
        import shap
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)
        
        # For binary classification, get the positive class SHAP values
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Class 1 (alive) probabilities
        
        # Create force plot
        fig = shap.force_plot(
            explainer.expected_value[1] if isinstance(explainer.expected_value, np.ndarray) else explainer.expected_value,
            shap_values[0],
            features.iloc[0],
            matplotlib=True,
            show=False
        )
        
        return fig
    except Exception as e:
        st.warning(f"Could not generate SHAP explanation: {str(e)}")
        return None

# Main app
def main():
    st.title("🏥 Sepsis Survival & Risk Prediction Platform")
    st.markdown("---")
    
    # Sidebar for information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This application predicts the risk of sepsis-related mortality 
        based on patient clinical parameters.
        
        **Input Parameters:**
        - **Age**: Patient age in years (18-100)
        - **Sex**: Patient biological sex
        - **Episode**: Number of sepsis episodes
        
        **Model**: Final Sepsis Survival Prediction Model
        **Features**: 4 engineered features with interactions
        """)
        
        st.markdown("---")
        st.subheader("Feature Importance")
        st.markdown("""
        Based on correlation analysis:
        
        1. **Age** (-0.17): Strongest predictor
           - Older patients → higher mortality risk
        
        2. **Age×Episode Interaction** (-0.09): 
           - Combined effect of age and episode frequency
        
        3. **Sex** (0.02): Minimal effect
        
        4. **Episode** (-0.006): Very weak effect
        """)

    # Main content
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📋 Patient Information")
        
        # Input fields
        age = st.slider(
            "Age (years)",
            min_value=18,
            max_value=100,
            value=50,
            step=1,
            help="Patient age in years"
        )
        
        sex = st.radio(
            "Biological Sex",
            options=["Male", "Female"],
            horizontal=True,
            help="Patient biological sex"
        )
        
        episode = st.number_input(
            "Number of Sepsis Episodes",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
            help="How many times has this patient had sepsis?"
        )
        
        # Display selected parameters
        st.markdown("### Selected Parameters:")
        st.write(f"• **Age**: {age} years")
        st.write(f"• **Sex**: {sex}")
        st.write(f"• **Episodes**: {episode}")

    with col2:
        st.subheader("🔍 Risk Assessment")
        
        # Load model and make prediction
        try:
            model = get_model()
            
            # Preprocess input using feature engineering module
            features = preprocess_patient_input(age, sex, episode)
            
            # Validate features
            is_valid, validation_message = validate_features(features)
            if not is_valid:
                st.error(f"Feature validation failed: {validation_message}")
                return
            
            # Make prediction using model utils
            prediction, survival_probability, mortality_probability = make_prediction(model, features)
            
            # Classify risk using model utils
            risk_label, risk_class = classify_mortality_risk(mortality_probability)
            
            # Display results
            st.markdown("### Prediction Result:")
            st.markdown(f"<h2 class='{risk_class}'>{risk_label}</h2>", 
                       unsafe_allow_html=True)
            
            st.markdown("### Mortality Probability:")
            
            # Probability gauge
            col_prob1, col_prob2 = st.columns([3, 1])
            with col_prob1:
                st.progress(mortality_probability)
            with col_prob2:
                st.metric("Mortality", f"{mortality_probability*100:.1f}%")
            
            # Also show survival probability for context
            st.markdown("---")
            st.metric("Survival Probability", f"{survival_probability*100:.1f}%")
            
            # Risk interpretation
            st.markdown("### 📊 Interpretation:")
            if mortality_probability >= 0.6:
                st.error(
                    f"⚠️ **High Risk** ({mortality_probability*100:.1f}%)\n\n"
                    "Patient has elevated mortality risk. "
                    "Recommend intensive monitoring and intervention."
                )
            elif mortality_probability >= 0.35:
                st.warning(
                    f"⚠️ **Moderate Risk** ({mortality_probability*100:.1f}%)\n\n"
                    "Patient shows moderate mortality risk. "
                    "Recommend close monitoring and supportive care."
                )
            else:
                st.success(
                    f"✅ **Low Risk** ({mortality_probability*100:.1f}%)\n\n"
                    "Patient has relatively lower mortality risk. "
                    "Continue standard care protocols."
                )
            
            # Add SHAP explanation section
            st.markdown("---")
            st.markdown("## 📊 Model Interpretability")
            
            st.markdown("### Feature Contribution Analysis (SHAP)")
            st.markdown("""
            SHAP (SHapley Additive exPlanations) shows how each feature contributes to the prediction.
            The force plot below visualizes which features push the prediction toward higher or lower mortality risk.
            """)
            
            try:
                with st.spinner("Generating SHAP explanation..."):
                    shap_fig = generate_shap_explanation(model, features)
                
                if shap_fig is not None:
                    st.pyplot(shap_fig, use_container_width=True)
                else:
                    st.info("SHAP explanation unavailable for this model type.")
                    
                    # Fallback: Manual feature explanation
                    st.markdown("### Feature-wise Impact:")
                    
                    col_feat1, col_feat2 = st.columns(2)
                    with col_feat1:
                        st.markdown(f"""
                        **Age**: {age} years
                        - Correlation: -0.17 (higher age → higher mortality)
                        - Impact: {"📈 High" if age > 65 else "📉 Low"}
                        """)
                        
                        st.markdown(f"""
                        **Sex**: {sex}
                        - Correlation: 0.02 (minimal effect)
                        - Impact: Very Small
                        """)
                    
                    with col_feat2:
                        st.markdown(f"""
                        **Episodes**: {episode}
                        - Correlation: -0.006 (very weak)
                        - Impact: Minimal
                        """)
                        
                        st.markdown(f"""
                        **Age × Episode**: {age} × {episode} = {age * episode}
                        - Correlation: -0.09 (moderate effect)
                        - Impact: {"📈 Moderate" if (age * episode) > 100 else "📉 Low"}
                        """)
            
            except Exception as e:
                st.warning(f"Error generating SHAP explanation: {str(e)}")
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            st.info("Please ensure the model file is properly loaded.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Sepsis Survival & Risk Prediction Platform | Final Project</p>
    <p>⚠️ Disclaimer: This tool is for educational and research purposes. 
    Do not use as a substitute for professional medical diagnosis.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
