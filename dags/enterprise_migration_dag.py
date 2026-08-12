from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default settings for the DAG
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'enterprise_cloud_migration_pipeline',
    default_args=default_args,
    description='End-to-End ELT Pipeline with Great Expectations & dbt',
    schedule_interval='@daily',
    start_date=datetime(2026,7, 1),
    catchup=False,
    tags=['migration', 'bigquery', 'ml'],
) as dag:

    # Task 1: Generate Legacy Data (Phase 1)
    generate_legacy_data = BashOperator(
        task_id='generate_legacy_data',
        bash_command='python /opt/airflow/scripts/01_generate_legacy_data.py',
    )

    # Task 2: Firewall & Quarantine (Phase 2)
    validate_data = BashOperator(
        task_id='validate_data_great_expectations',
        bash_command='python /opt/airflow/scripts/02_validate_and_quarantine.py',
    )

    # Task 3: Extract & Load to BigQuery (Phase 3a)
    load_to_bq = BashOperator(
        task_id='load_to_bigquery',
        bash_command='python /opt/airflow/scripts/03_load_to_bigquery.py',
    )
    # Task 3.5: Post-Load Reconciliation (Layer 3 Audit)
    audit_pipeline = BashOperator(
        task_id='audit_pipeline_parity',
        bash_command='python /opt/airflow/scripts/05_pipeline_audit.py',
    )
    # Task 4: Transform via dbt (Phase 3b)
    dbt_transform = BashOperator(
        task_id='dbt_run_and_test',
        # Change directory to the dbt project, run models, then run tests
        bash_command='cd /opt/airflow/enterprise_warehouse && dbt run --profiles-dir . && dbt test --profiles-dir .',
    )

    # Task 5: ML Risk Engine (Phase 4)
    run_ml_risk_engine = BashOperator(
        task_id='run_anomaly_detection',
        bash_command='python /opt/airflow/scripts/04_anomaly_detection.py',
    )

    # Define the Execution Order (The Pipeline Architecture)
    generate_legacy_data >> validate_data >> load_to_bq >> audit_pipeline >> dbt_transform >> run_ml_risk_engine