import pandas as pd
import json
import os

def clean_data():
    print("Data Transformation Started")
    
    # Create processed directory
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. Clean Stripe (Users) Data
    stripe_file = "data/raw/stripe/users.json"
    if os.path.exists(stripe_file):
        print("Cleaning Stripe Data...")
        with open(stripe_file, "r") as f:
            stripe_data = json.load(f)
            
        df_stripe = pd.json_normalize(stripe_data)
        
        # Keep only essential columns and rename them to a unified schema
        cols_to_keep = ['id', 'name', 'email', 'phone', 'company.name']
        
        # Only keep existing columns to avoid key errors
        available_cols = [c for c in cols_to_keep if c in df_stripe.columns]
        df_stripe = df_stripe[available_cols]
        
        # Rename columns to standardized schema
        df_stripe.rename(columns={
            'id': 'user_id',
            'company.name': 'company_name'
        }, inplace=True)
        
        # Handle Nulls
        df_stripe.fillna("N/A", inplace=True)
        
        # Save to processed as CSV
        stripe_output = os.path.join(processed_dir, "cleaned_stripe_users.csv")
        df_stripe.to_csv(stripe_output, index=False)
        print(f"Stripe Data cleaned and saved to {stripe_output}")
    else:
        print("No Stripe raw data found. Skipping.")

    # 2. Clean Salesforce (Posts) Data
    salesforce_file = "data/raw/salesforce/posts.json"
    if os.path.exists(salesforce_file):
        print("Cleaning Salesforce Data...")
        with open(salesforce_file, "r") as f:
            salesforce_data = json.load(f)
            
        df_salesforce = pd.DataFrame(salesforce_data)
        
        # Keep essential columns and rename
        cols_to_keep = ['id', 'userId', 'title']
        available_cols = [c for c in cols_to_keep if c in df_salesforce.columns]
        df_salesforce = df_salesforce[available_cols]
        
        df_salesforce.rename(columns={
            'id': 'post_id',
            'userId': 'user_id',
            'title': 'post_title'
        }, inplace=True)
        
        # Clean text
        df_salesforce['post_title'] = df_salesforce['post_title'].str.title()
        
        # Save to processed as CSV
        salesforce_output = os.path.join(processed_dir, "cleaned_salesforce_posts.csv")
        df_salesforce.to_csv(salesforce_output, index=False)
        print(f"Salesforce Data cleaned and saved to {salesforce_output}")
    else:
        print("No Salesforce raw data found. Skipping.")

    # 3. Clean Zendesk (Tickets) Data
    zendesk_file = "data/raw/zendesk/tickets.json"
    if os.path.exists(zendesk_file):
        print("Cleaning Zendesk Data...")
        with open(zendesk_file, "r") as f:
            zendesk_data = json.load(f)
            
        df_zendesk = pd.DataFrame(zendesk_data)
        
        # Ensure all required columns are there, fill missing
        df_zendesk.fillna("N/A", inplace=True)
        
        # Save to processed as CSV
        zendesk_output = os.path.join(processed_dir, "cleaned_zendesk_tickets.csv")
        df_zendesk.to_csv(zendesk_output, index=False)
        print(f"Zendesk Data cleaned and saved to {zendesk_output}")
    else:
        print("No Zendesk raw data found. Skipping.")
        
    print("Data Transformation Completed")

if __name__ == "__main__":
    clean_data()
