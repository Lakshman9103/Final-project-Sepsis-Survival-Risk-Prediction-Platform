"""
Data Preprocessing Module

This module handles loading and cleaning of sepsis survival data.
Converts from raw dataset to cleaned format with proper column names and encodings.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_data(filepath: str) -> pd.DataFrame:
    """
    Load raw sepsis dataset from CSV.
    
    Args:
        filepath: Path to the raw CSV file
        
    Returns:
        DataFrame with raw data
        
    Example:
        >>> df = load_raw_data("data/sepsis_survival_primary_cohort.csv")
    """
    df = pd.read_csv(filepath)
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename long column names to shorter, more usable names.
    
    Args:
        df: DataFrame with original column names
        
    Returns:
        DataFrame with renamed columns
        
    Column Mapping:
        - age_years → age
        - sex_0male_1female → sex
        - episode_number → episode
        - hospital_outcome_1alive_0dead → outcome
    """
    column_mapping = {
        "age_years": "age",
        "sex_0male_1female": "sex",
        "episode_number": "episode",
        "hospital_outcome_1alive_0dead": "outcome"
    }
    
    df = df.rename(columns=column_mapping)
    return df


def encode_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert categorical values to meaningful labels.
    
    Args:
        df: DataFrame with raw categorical values
        
    Returns:
        DataFrame with decoded categorical values
        
    Encoding:
        - sex: 0 → 'male', 1 → 'female'
        - outcome: 0 → 'dead', 1 → 'alive'
    """
    df_copy = df.copy()
    
    # Decode sex
    if 'sex' in df_copy.columns:
        df_copy['sex'] = df_copy['sex'].map({0: 'male', 1: 'female'})
    
    # Decode outcome
    if 'outcome' in df_copy.columns:
        df_copy['outcome'] = df_copy['outcome'].map({0: 'dead', 1: 'alive'})
    
    return df_copy


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    """
    Check for missing values in the dataset.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Series with missing value counts per column
    """
    return df.isnull().sum()


def get_data_info(df: pd.DataFrame) -> dict:
    """
    Get basic information about the dataset.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with dataset info (shape, columns, missing values, etc.)
    """
    info = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    return info


def preprocess_raw_data(filepath: str) -> pd.DataFrame:
    """
    Complete preprocessing pipeline for raw data.
    
    Args:
        filepath: Path to raw CSV file
        
    Returns:
        Fully preprocessed DataFrame ready for EDA
    """
    # Load data
    df = load_raw_data(filepath)
    
    # Rename columns
    df = rename_columns(df)
    
    # Encode categorical values
    df = encode_categorical_values(df)
    
    return df


if __name__ == "__main__":
    # Example usage
    filepath = "data/s41598-020-73558-3_sepsis_survival_dataset/s41598-020-73558-3_sepsis_survival_primary_cohort.csv"
    
    print("Loading and preprocessing data...")
    df = preprocess_raw_data(filepath)
    
    print("\nDataset Info:")
    info = get_data_info(df)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nFirst few rows:\n{df.head()}")
