"""
Feature Engineering Module

This module handles creation and engineering of features from raw sepsis data.
Implements feature transformations ready for machine learning models.
"""

import pandas as pd
import numpy as np


def encode_sex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert sex from categorical (male/female) to numeric (0/1).
    
    Args:
        df: DataFrame with 'sex' column (male/female strings)
        
    Returns:
        DataFrame with numeric sex encoding
        
    Encoding:
        - male → 0
        - female → 1
    """
    df_copy = df.copy()
    sex_mapping = {'male': 0, 'female': 1}
    df_copy['sex'] = df_copy['sex'].map(sex_mapping)
    return df_copy


def create_age_risk_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create age-based risk categories through binning.
    
    Args:
        df: DataFrame with 'age' column
        
    Returns:
        DataFrame with new 'age_risk' column
        
    Risk Categories:
        - 0: Low risk (0-40 years)
        - 1: Moderate risk (40-60 years)
        - 2: High risk (60-75 years)
        - 3: Very high risk (75+ years)
    """
    df_copy = df.copy()
    
    df_copy['age_risk'] = pd.cut(
        df_copy['age'],
        bins=[0, 40, 60, 75, 120],
        labels=[0, 1, 2, 3],
        include_lowest=True
    )
    
    df_copy['age_risk'] = df_copy['age_risk'].astype(int)
    
    return df_copy


def create_episode_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create episode frequency categories through binning.
    
    Args:
        df: DataFrame with 'episode' column
        
    Returns:
        DataFrame with new 'episode_category' column
        
    Episode Categories:
        - 0: First episode (1)
        - 1: Repeated episodes (2-3)
        - 2: Frequent episodes (4+)
    """
    df_copy = df.copy()
    
    df_copy['episode_category'] = pd.cut(
        df_copy['episode'],
        bins=[0, 1, 3, 10],
        labels=[0, 1, 2],
        include_lowest=True
    )
    
    df_copy['episode_category'] = df_copy['episode_category'].astype(int)
    
    return df_copy


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction features between age and episode.
    
    Args:
        df: DataFrame with 'age' and 'episode' columns
        
    Returns:
        DataFrame with new 'age_episode_interaction' column
        
    Feature:
        - age_episode_interaction = age × episode
        Captures combined effect of age and episode persistence
    """
    df_copy = df.copy()
    df_copy['age_episode_interaction'] = df_copy['age'] * df_copy['episode']
    return df_copy


def select_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select features for machine learning model.
    
    Args:
        df: DataFrame with all features including target
        
    Returns:
        DataFrame with only model features (excluding outcome)
        
    Selected Features:
        - age: Patient age in years
        - sex: Biological sex (0=male, 1=female)
        - episode: Number of sepsis episodes
        - age_episode_interaction: Combined age and episode effect
        - outcome: Target variable (0=dead, 1=alive)
    """
    feature_columns = ['age', 'sex', 'episode', 'age_episode_interaction', 'outcome']
    
    # Filter to only available columns
    available_columns = [col for col in feature_columns if col in df.columns]
    
    return df[available_columns]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete feature engineering pipeline.
    
    Args:
        df: DataFrame with raw columns (age, sex, episode, outcome)
        
    Returns:
        DataFrame with engineered features ready for modeling
        
    Operations:
        1. Encode sex (categorical → numeric)
        2. Create age risk categories
        3. Create episode categories
        4. Create interaction features
        5. Select final model features
    """
    # Encode categorical variables
    df = encode_sex(df)
    
    # Create binned features
    df = create_age_risk_categories(df)
    df = create_episode_categories(df)
    
    # Create interaction features
    df = create_interaction_features(df)
    
    # Select final features
    df = select_model_features(df)
    
    return df


def get_feature_correlations(df: pd.DataFrame) -> dict:
    """
    Calculate feature correlations with target variable.
    
    Args:
        df: DataFrame with numeric features and 'outcome' column
        
    Returns:
        Dictionary with feature names and their correlations with outcome
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corr()['outcome'].to_dict()
    return correlations


def get_feature_info() -> dict:
    """
    Return information about engineered features.
    
    Returns:
        Dictionary with feature descriptions and importance
    """
    info = {
        'features': {
            'age': {
                'description': 'Patient age in years',
                'type': 'continuous',
                'correlation_with_outcome': -0.17,
                'importance': 'highest'
            },
            'sex': {
                'description': 'Biological sex (0=male, 1=female)',
                'type': 'categorical',
                'correlation_with_outcome': 0.02,
                'importance': 'minimal'
            },
            'episode': {
                'description': 'Number of sepsis episodes',
                'type': 'continuous',
                'correlation_with_outcome': -0.006,
                'importance': 'very_weak'
            },
            'age_episode_interaction': {
                'description': 'Interaction: age × episode',
                'type': 'continuous',
                'correlation_with_outcome': -0.09,
                'importance': 'moderate'
            }
        },
        'interpretation': {
            'age_correlation': 'Negative correlation means older patients have higher mortality risk',
            'negative_values': 'Negative correlations indicate higher age/episode values correlate with death (outcome=0)',
            'interaction': 'Combined effect of age and episode frequency'
        }
    }
    return info


if __name__ == "__main__":
    # Example usage
    # Assuming preprocessed data is available
    df = pd.read_csv("data/sepsis_EDA.csv")
    
    print("Engineering features...")
    df_engineered = engineer_features(df)
    
    print(f"\nShape after feature engineering: {df_engineered.shape}")
    print(f"\nFirst few rows:\n{df_engineered.head()}")
    
    print("\nFeature Correlations with Outcome:")
    correlations = get_feature_correlations(df_engineered)
    for feature, corr in correlations.items():
        print(f"  {feature}: {corr:.4f}")
    
    print("\nFeature Information:")
    info = get_feature_info()
    for feature, details in info['features'].items():
        print(f"\n{feature}:")
        for key, value in details.items():
            print(f"  {key}: {value}")
