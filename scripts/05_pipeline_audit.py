import pandas as pd
from google.cloud import bigquery
import sys
import os

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "gcp_service_account.json")
PROJECT_ID = "enterprise-migration-portfolio" 

def run_audit():
    print("Starting Layer 3: Executive Post-Load Audit...")
    
    # 1. Get the local ground truth (Cleaned Parquet before upload)
    parquet_path = os.path.join(BASE_DIR, "data", "clean", "Project_Financials.parquet")
    df_local = pd.read_parquet(parquet_path)
    
    local_total_billed = df_local['BilledAmount'].sum()
    local_row_count = len(df_local)

    # 2. Get the cloud truth (Raw BigQuery Load)
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT 
            SUM(BilledAmount) as total_billed, 
            COUNT(*) as row_count 
        FROM `{PROJECT_ID}.raw_erp_data.Project_Financials`
    """
    df_cloud = client.query(query).to_dataframe()
    
    cloud_total_billed = df_cloud['total_billed'].iloc[0]
    cloud_row_count = df_cloud['row_count'].iloc[0]

    # 3. The Reconciliation Test
    print(f"Local Parquet - Rows: {local_row_count}, Total Billed: ${local_total_billed:,.2f}")
    print(f"Cloud BQ      - Rows: {cloud_row_count}, Total Billed: ${cloud_total_billed:,.2f}")

    # We use round(..., 2) to prevent floating point mismatch errors
    if local_row_count == cloud_row_count and round(local_total_billed, 2) == round(cloud_total_billed, 2):
        print("✅ AUDIT PASS: 100% Data Parity achieved between on-premise and cloud.")
    else:
        print("❌ AUDIT FAIL: Data mismatch detected! Halting pipeline.")
        sys.exit(1)  # This exit code tells Airflow to instantly fail the task and turn red

if __name__ == "__main__":
    run_audit()