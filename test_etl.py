import pytest
import pandas as pd
import json
import os
from transformation.clean_data import clean_data
from extraction.stripe_extractor import extract_stripe_data

def test_stripe_extraction_creates_file():
    # Remove file if exists to test extraction
    test_file = "data/raw/stripe/users.json"
    if os.path.exists(test_file):
        os.remove(test_file)
        
    extract_stripe_data()
    
    assert os.path.exists(test_file)
    with open(test_file, 'r') as f:
        data = json.load(f)
        assert len(data) > 0
        # Verify website field is removed
        assert "website" not in data[0]

def test_transformation_cleans_stripe_data():
    # Ensure extraction ran first
    extract_stripe_data()
    
    # Run transformation
    clean_data()
    
    processed_file = "data/processed/cleaned_stripe_users.csv"
    assert os.path.exists(processed_file)
    
    df = pd.read_csv(processed_file)
    
    # Check expected columns exist
    expected_cols = ['user_id', 'name', 'email', 'phone', 'company_name']
    for col in expected_cols:
        assert col in df.columns
        
    # Check nulls are handled (should be 0 nulls because of fillna)
    assert df.isnull().sum().sum() == 0

def test_transformation_cleans_salesforce_data():
    processed_file = "data/processed/cleaned_salesforce_posts.csv"
    
    # Only test if file exists (meaning extraction ran)
    if os.path.exists(processed_file):
        df = pd.read_csv(processed_file)
        expected_cols = ['post_id', 'user_id', 'post_title']
        for col in expected_cols:
            assert col in df.columns
            
        # Check title formatting (Title Case)
        sample_title = df['post_title'].iloc[0]
        assert sample_title == sample_title.title()
