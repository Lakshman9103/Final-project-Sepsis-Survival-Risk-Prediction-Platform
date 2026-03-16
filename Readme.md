# 🏥 Sepsis Survival & Risk Prediction Platform

## Project Overview
This is a machine learning-based predictive system for assessing sepsis-related mortality risk using patient clinical parameters. The platform includes data processing, model training with MLflow tracking, and a production-ready Streamlit web application.

## 📁 Project Structure
```
├── app/
│   └── app.py                 # Streamlit web application
├── data/
│   ├── sepsis_clean.csv
│   ├── sepsis_EDA.csv
│   ├── sepsis_model_data.csv  # Processed data for modeling
│   └── s41598-020-73558-3_sepsis_survival_dataset/
├── models/
│   ├── sepsis_best_model.pkl
│   └── sepsis_final_model.pkl # 👈 Used in Streamlit app
├── notebook/
│   ├── Datapreprossing.ipynb
│   ├── EDA.ipynb
│   ├── Featurengineering.ipynb
│   ├── modeltraining.ipynb
│   ├── MlFlow.ipynb           # MLflow experiment tracking
│   └── models/                # Pre-trained models
├── Requirements.txt           # Python dependencies
├── setup.py
└── run_app.py                 # Quick start script for Streamlit app
```

## 🔧 Installation

### 1. Install Dependencies
```bash
pip install -r Requirements.txt
```

### 2. Verify Model Files
Ensure the following model files exist:
- `models/sepsis_final_model.pkl` ✅ (Used by Streamlit app)
- `notebook/models/` (4 models used for MLflow comparison)

## 🚀 Running the Streamlit App

### Option 1: Quick Start (Recommended)
```bash
python run_app.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run app/app.py
```

The app will open in your browser at: **http://localhost:8501**

## 📊 Features

### Input Parameters
- **Age**: Patient age (18-100 years)
- **Sex**: Male or Female
- **Episodes**: Number of previous sepsis episodes (1-20)

### Preprocessing Pipeline
The app automatically applies the same preprocessing used during model training:
1. Sex encoding (Male=0, Female=1)
2. Age risk grouping (4 categories based on age bins)
3. Episode category classification (3 categories)
4. Age × Episode interaction feature

### Output
- **Risk Classification**: Low/Moderate/High Risk
- **Mortality Probability**: 0-100%
- **Risk Interpretation**: Contextual medical guidance

## 📈 Model Information

### Training Details (from MlFlow)
- **Training Data**: `sepsis_model_data.csv`
- **Features**: age, sex, episode, age_episode_interaction (4 features)
- **Target**: outcome (binary classification)
- **Train/Test Split**: 80/20 with stratification

### Models Trained
1. Logistic Regression
2. Random Forest
3. XGBoost
4. CatBoost

### Best Model
- **Primary Model**: `sepsis_final_model.pkl`
- **Metrics Tracked**: Accuracy, Recall, ROC-AUC

## 📓 Notebooks Guide

| Notebook | Purpose |
|----------|---------|
| `Datapreprossing.ipynb` | Data cleaning and preprocessing |
| `EDA.ipynb` | Exploratory data analysis |
| `Featurengineering.ipynb` | Feature engineering and selection |
| `modeltraining.ipynb` | Model training and evaluation |
| `MlFlow.ipynb` | MLflow experiment tracking |

## 🔬 Feature Engineering Details

### Key Features Created
1. **age_risk**: Age-based risk categorization
   - 0: Low risk (0-40 years)
   - 1: Moderate risk (40-60 years)
   - 2: High risk (60-75 years)
   - 3: Very high risk (75+ years)

2. **episode_category**: Episode frequency categorization
   - 0: First episode (1)
   - 1: Repeated episodes (2-3)
   - 2: Frequent episodes (4+)

3. **age_episode_interaction**: Combined effect of age and episode frequency

### Feature Importance (Correlation with Outcome)
- Age: -0.17 (strongest predictor)
- Age × Episode: -0.09
- Sex: 0.02 (minimal effect)
- Episode: -0.006 (very weak)


---
**Last Updated**: March 2026
