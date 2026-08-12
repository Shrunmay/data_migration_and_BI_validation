import os
import pandas as pd
import numpy as np
from google.cloud import bigquery
from sklearn.ensemble import IsolationForest

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "gcp_service_account.json")

PROJECT_ID = "enterprise-migration-portfolio" # Ensure this matches your hyphenated ID
READ_DATASET = "analytics_dev"
WRITE_DATASET = "analytics_dev"

print("Initializing Phase 4: Machine Learning Risk Engine...")

def run_risk_engine():
    client = bigquery.Client(project=PROJECT_ID)
    
    # 1. Extract the clean Fact table from BigQuery
    print("Extracting Star Schema Fact Table...")
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{READ_DATASET}.fct_project_financials`
    """
    df_fact = client.query(query).to_dataframe()
    
    # 2. Feature Engineering
    # We are looking for anomalies in the relationship between cost, delay, and budget burn.
    features = ['billed_amount', 'delivery_delay_weeks', 'cost_to_date_pct_budget']
    X = df_fact[features].fillna(0)
    
    # 3. Initialize & Train the Isolation Forest
    # Setting contamination to 0.01 means we are explicitly hunting for the top 1% most severe anomalies
    print("Training Isolation Forest Model (Targeting top 1% risk)...")
    model = IsolationForest(
        n_estimators=200, 
        contamination=0.01, 
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X)
    
    # 4. Generate Risk Scores
    raw_scores = model.decision_function(X)
    min_score = np.min(raw_scores)
    max_score = np.max(raw_scores)
    
    # Normalize the abstract ML output into a readable 0-100 Risk Index
    risk_index = ((max_score - raw_scores) / (max_score - min_score)) * 100
    df_fact['ml_risk_score'] = np.round(risk_index, 2)
    
    # Flag the absolute highest risks based on our contamination threshold
    predictions = model.predict(X)
    df_fact['is_critical_anomaly'] = (predictions == -1)
    
    anomalies_found = df_fact['is_critical_anomaly'].sum()
    print(f"ML Processing Complete: Flagged {anomalies_found} high-risk transactions.")
    
    # 5. Load the enriched data back to BigQuery for Power BI
    table_id = f"{PROJECT_ID}.{WRITE_DATASET}.fct_financials_risk_scored"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    print(f"Uploading enriched Risk Data to BigQuery ({table_id})...")
    job = client.load_table_from_dataframe(df_fact, table_id, job_config=job_config)
    job.result()
    
    print("SUCCESS: Phase 4 Complete. Risk Intelligence table is ready for visualization.")

if __name__ == "__main__":
    run_risk_engine()