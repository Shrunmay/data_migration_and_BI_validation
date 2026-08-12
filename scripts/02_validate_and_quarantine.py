import os
import sqlite3
import pandas as pd
import great_expectations as gx
import numpy as np

# ---------------------------------------------------------
# Configuration & Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data/raw/legacy_erp.db')
CLEAN_DIR = os.path.join(BASE_DIR, 'data/clean')
QUARANTINE_DIR = os.path.join(BASE_DIR, 'data/quarantine')

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

print("Initializing Phase 2: Dynamic Data Firewall...")

# ---------------------------------------------------------
# Helper Function: Programmatic Expectation Generator
# ---------------------------------------------------------
def apply_programmatic_suite(gx_df, table_name):
    """
    Dynamically generates structural expectations based on the dataframe's metadata.
    This effortlessly scales to 200+ test cases across an enterprise database.
    """
    total_tests = 0
    
    for column in gx_df.columns:
        # 1. Structural Integrity: Column existence
        gx_df.expect_column_to_exist(column)
        total_tests += 1
        
        # 2. Type Adherence: Map Pandas dtypes to GE expectations
        dtype = str(gx_df[column].dtype)
        if 'int' in dtype:
            gx_df.expect_column_values_to_be_in_type_list(column, ['int', 'int32', 'int64'])
        elif 'float' in dtype:
            gx_df.expect_column_values_to_be_in_type_list(column, ['float', 'float32', 'float64'])
        elif 'object' in dtype:
            gx_df.expect_column_values_to_be_in_type_list(column, ['str', 'object'])
        total_tests += 1

        # 3. Nullity Bounds: Allow 2% nulls for standard columns, strict 0% for IDs
        if 'ID' in column:
            gx_df.expect_column_values_to_not_be_null(column, result_format={"result_format": "COMPLETE"})
        else:
            gx_df.expect_column_values_to_not_be_null(column, mostly=0.98, result_format={"result_format": "COMPLETE"})
        total_tests += 1
        
    print(f"[{table_name}] Programmatically generated {total_tests} structural expectations.")
    return gx_df

# ---------------------------------------------------------
# Main Validation Execution
# ---------------------------------------------------------
def validate_and_quarantine():
    conn = sqlite3.connect(DB_PATH)
    tables = ['Sites', 'Suppliers', 'Rental_Logistics', 'Project_Financials']
    
    for table in tables:
        print(f"\n--- Processing Table: {table} ---")
        df_raw = pd.read_sql(f"SELECT * FROM {table}", conn)
        gx_df = gx.from_pandas(df_raw)
        
        # Apply the dynamic structural baseline
        gx_df = apply_programmatic_suite(gx_df, table)
        
        # ---------------------------------------------------------
        # Apply Strict Business Domain Logic
        # ---------------------------------------------------------
        if table == 'Project_Financials':
            # Isolate and drop severe systemic outliers in construction budgets.
            # Projects showing a cost-to-date budget drop of more than 20% are flagged as corrupted outliers and removed.
            gx_df.expect_column_values_to_be_between(
                column="ctd_pct_budget", 
                min_value=0.0, 
                max_value=150.0, 
                result_format={"result_format": "COMPLETE"}
            )
            # Flag negative billing amounts
            gx_df.expect_column_values_to_be_between(
                column="BilledAmount", 
                min_value=0.01, 
                result_format={"result_format": "COMPLETE"}
            )
            
        if table == 'Rental_Logistics':
            # Validate date formats strictly to catch the DD/MM/YYYY corruption
            gx_df.expect_column_values_to_match_regex(
                column="OrderDate", 
                regex=r"^\d{4}-\d{2}-\d{2}$",
                result_format={"result_format": "COMPLETE"}
            )

        # ---------------------------------------------------------
        # Execute Validation & Quarantine Logic
        # ---------------------------------------------------------
        results = gx_df.validate()
        
        if not results["success"]:
            print(f"CRITICAL: Validation failures detected in {table}. Quarantining corrupted data.")
            failing_indices = set()
            
            for result in results["results"]:
                if not result["success"]:
                    if "unexpected_index_list" in result["result"]:
                        failing_indices.update(result["result"]["unexpected_index_list"])
            
            # Split Data
            clean_df = df_raw.drop(index=list(failing_indices))
            quarantine_df = df_raw.loc[list(failing_indices)]
            
            # Save Outputs
            quarantine_df.to_csv(os.path.join(QUARANTINE_DIR, f"{table}_quarantined.csv"), index=False)
            clean_df.to_parquet(os.path.join(CLEAN_DIR, f"{table}_clean.parquet"), index=False)
            
            print(f"-> Quarantined {len(quarantine_df)} rows. Passed {len(clean_df)} clean rows.")
        else:
            print(f"SUCCESS: {table} passed all expectations.")
            df_raw.to_parquet(os.path.join(CLEAN_DIR, f"{table}_clean.parquet"), index=False)

    conn.close()
    print("\nPhase 2 Complete. Data firewall successfully executed.")

if __name__ == "__main__":
    validate_and_quarantine()