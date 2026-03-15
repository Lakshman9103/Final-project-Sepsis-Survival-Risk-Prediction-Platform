"""
Model Utilities Module

This module handles model loading, prediction, and inference operations.
Works with pre-trained models saved as pickle files.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict


def load_model(model_path: str):
    """
    Load a pre-trained model from disk.
    
    Args:
        model_path: Path to the pickle file containing the model
        
    Returns:
        Loaded model object
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        
    Example:
        >>> model = load_model("models/sepsis_final_model.pkl")
    """
    model_path = Path(model_path)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    model = joblib.load(str(model_path))
    return model


def make_prediction(model, features: pd.DataFrame) -> Tuple[int, float, float]:
    """
    Make a prediction using the loaded model.
    
    Args:
        model: Pre-trained model object
        features: DataFrame with model features (4 features for this model)
                 Columns: [age, sex, episode, age_episode_interaction]
        
    Returns:
        Tuple of:
            - prediction (int): 0=dead, 1=alive
            - survival_probability (float): Probability of survival (0-1)
            - mortality_probability (float): Probability of mortality (0-1)
            
    Example:
        >>> prediction, survival_prob, mortality_prob = make_prediction(model, features)
        >>> print(f"Mortality Risk: {mortality_prob*100:.1f}%")
    """
    # Get class prediction
    prediction = model.predict(features)[0]
    
    # Get probability for alive (class 1)
    survival_probability = float(model.predict_proba(features)[0][1])
    
    # Calculate mortality probability (inverse of survival)
    mortality_probability = 1 - survival_probability
    
    return int(prediction), survival_probability, mortality_probability


def batch_predict(model, features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Make predictions on multiple samples.
    
    Args:
        model: Pre-trained model object
        features_df: DataFrame with rows of features (n_samples × n_features)
        
    Returns:
        DataFrame with columns: prediction, survival_prob, mortality_prob
    """
    predictions = model.predict(features_df)
    probabilities = model.predict_proba(features_df)
    
    results = pd.DataFrame({
        'prediction': predictions,
        'survival_probability': probabilities[:, 1],
        'mortality_probability': 1 - probabilities[:, 1]
    })
    
    return results


def get_model_info(model) -> Dict:
    """
    Get information about the loaded model.
    
    Args:
        model: Loaded model object
        
    Returns:
        Dictionary with model information (type, parameters, etc.)
    """
    info = {
        'model_type': type(model).__name__,
        'model_class': str(type(model)),
        'parameters': model.get_params() if hasattr(model, 'get_params') else None,
        'has_proba': hasattr(model, 'predict_proba'),
        'feature_names': getattr(model, 'feature_names_in_', None),
        'n_classes': len(model.classes_) if hasattr(model, 'classes_') else None,
        'classes': getattr(model, 'classes_', None)
    }
    return info


def classify_mortality_risk(mortality_probability: float) -> Tuple[str, str]:
    """
    Classify mortality risk based on probability.
    
    Args:
        mortality_probability: Probability of mortality (0-1)
        
    Returns:
        Tuple of:
            - risk_label (str): Display label with emoji (e.g., "🔴 High Risk")
            - risk_class (str): CSS class for styling
            
    Risk Thresholds:
        - High Risk: ≥60% mortality
        - Moderate Risk: 35-60% mortality
        - Low Risk: <35% mortality
    """
    if mortality_probability >= 0.6:
        return "🔴 High Risk", "risk-high"
    elif mortality_probability >= 0.35:
        return "🟠 Moderate Risk", "risk-moderate"
    else:
        return "🟢 Low Risk", "risk-low"


def validate_features(features: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that features have the correct shape and values.
    
    Args:
        features: DataFrame with features to validate
        
    Returns:
        Tuple of:
            - is_valid (bool): Whether validation passed
            - message (str): Validation message
    """
    expected_features = ['age', 'sex', 'episode', 'age_episode_interaction']
    expected_shape = (1, 4)
    
    # Check shape
    if features.shape != expected_shape:
        return False, f"Expected shape {expected_shape}, got {features.shape}"
    
    # Check columns
    if set(features.columns) != set(expected_features):
        return False, f"Expected columns {expected_features}, got {list(features.columns)}"
    
    # Check for NaN values
    if features.isnull().any().any():
        return False, "Features contain NaN values"
    
    # Check numeric types
    for col in features.columns:
        if not np.issubdtype(features[col].dtype, np.number):
            return False, f"Column '{col}' is not numeric"
    
    # Check value ranges
    if features['age'].values[0] < 0 or features['age'].values[0] > 120:
        return False, "Age out of valid range (0-120)"
    
    if not features['sex'].isin([0, 1]).all():
        return False, "Sex must be 0 (male) or 1 (female)"
    
    if features['episode'].values[0] < 1:
        return False, "Episode count must be >= 1"
    
    return True, "Features are valid"


if __name__ == "__main__":
    # Example usage
    print("Model utilities module")
    print("\nAvailable functions:")
    print("  - load_model(model_path)")
    print("  - make_prediction(model, features)")
    print("  - batch_predict(model, features_df)")
    print("  - get_model_info(model)")
    print("  - classify_mortality_risk(mortality_probability)")
    print("  - validate_features(features)")
