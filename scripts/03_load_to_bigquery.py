import os
import pandas as pd
from google.cloud import bigquery

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CLEAN_DIR = os.path.join(BASE_DIR, 'data/clean')

# TODO: Replace with your actual GCP Project ID
PROJECT_ID = "enterprise-migration-portfolio" 
DATASET_ID = "raw_erp_data"

# Authenticate using the local service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "gcp_service_account.json")

print("Initializing Phase 3: BigQuery Ingestion...")

def load_parquet_to_bq():
    client = bigquery.Client(project=PROJECT_ID)
    tables = ['Sites', 'Suppliers', 'Rental_Logistics', 'Project_Financials']
    
    for table in tables:
        parquet_path = os.path.join(CLEAN_DIR, f"{table}_clean.parquet")
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table}"
        
        print(f"Reading clean data for {table}...")
        df = pd.read_parquet(parquet_path)
        
        # Configure the load job to overwrite the table if it already exists
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )
        
        print(f"Uploading {len(df)} rows to BigQuery ({table_id})...")
        try:
            job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result() # Wait for the job to complete
            print(f"SUCCESS: {table} loaded to BigQuery.\n")
        except Exception as e:
            print(f"FATAL ERROR: Failed to load {table}. Details: {e}\n")

if __name__ == "__main__":
    load_parquet_to_bq()