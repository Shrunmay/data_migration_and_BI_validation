import os
import sqlite3
import pandas as pd
import numpy as np
from faker import Faker

# Initialization
fake = Faker()
Faker.seed(42)
np.random.seed(42)

# Volumetrics
NUM_SITES = 500
NUM_SUPPLIERS = 150
NUM_TRANSACTIONS = 100000

print("Initializing Legacy ERP Data Generation...")

# ---------------------------------------------------------
# 1. GENERATE MASTER DATA
# ---------------------------------------------------------
print("Generating Sites and Suppliers...")
sites = pd.DataFrame({
    'SiteID': range(1, NUM_SITES + 1),
    'ProjectName': [fake.company() + " Site" for _ in range(NUM_SITES)],
    'Region': [fake.state() for _ in range(NUM_SITES)],
    'Status': np.random.choice(['Active', 'Completed', 'Suspended'], NUM_SITES, p=[0.8, 0.15, 0.05])
})

suppliers = pd.DataFrame({
    'SupplierID': range(1, NUM_SUPPLIERS + 1),
    'VendorName': [fake.company() for _ in range(NUM_SUPPLIERS)],
    'BaseRiskScore': np.random.uniform(1.0, 10.0, NUM_SUPPLIERS),
    # 10% probability of an active disruption at the supplier level
    'IsDisrupted': np.random.choice([True, False], NUM_SUPPLIERS, p=[0.10, 0.90])
})

# ---------------------------------------------------------
# 2. GENERATE OPERATIONAL DATA (Logistics)
# ---------------------------------------------------------
print("Generating Rental Logistics...")
logistics = pd.DataFrame({
    'LogisticsID': range(1, NUM_TRANSACTIONS + 1),
    'SiteID': np.random.choice(sites['SiteID'], NUM_TRANSACTIONS),
    'SupplierID': np.random.choice(suppliers['SupplierID'], NUM_TRANSACTIONS),
    'EquipmentType': np.random.choice(['Excavator', 'Crane', 'Dozer', 'Scissor Lift', 'Generator'], NUM_TRANSACTIONS),
    'OrderDate': [fake.date_between(start_date='-3y', end_date='today') for _ in range(NUM_TRANSACTIONS)],
    'BaseRentalCost': np.round(np.random.uniform(500, 15000, NUM_TRANSACTIONS), 2)
})

# Merge supplier disruption logic to calculate actual delivery delay
logistics = logistics.merge(suppliers[['SupplierID', 'IsDisrupted']], on='SupplierID', how='left')

# Normal delay is 1-2 weeks. If disrupted, it results in a 5+ week order block.
logistics['DeliveryDelayWeeks'] = np.where(
    logistics['IsDisrupted'],
    np.random.randint(5, 12, NUM_TRANSACTIONS),
    np.random.randint(1, 3, NUM_TRANSACTIONS)
)
logistics = logistics.drop(columns=['IsDisrupted'])

# ---------------------------------------------------------
# 3. GENERATE FINANCIAL DATA (Budgets)
# ---------------------------------------------------------
print("Generating Project Financials...")
financials = pd.DataFrame({
    'RecordID': range(1, NUM_TRANSACTIONS + 1),
    'LogisticsID': logistics['LogisticsID'],
    'BilledAmount': logistics['BaseRentalCost'] * np.random.uniform(0.9, 1.2, NUM_TRANSACTIONS),
    'ctd_pct_budget': np.random.uniform(10.0, 95.0, NUM_TRANSACTIONS) # Cost-to-Date % of Budget
})

# ---------------------------------------------------------
# 4. INJECT ANOMALIES & MESSY DATA
# ---------------------------------------------------------
print("Injecting systemic corruption and anomalies...")

# Anomaly 1: The >20% ctd_pct_budget drop. 
# Simulating a massive systemic error where cost-to-date mathematically implodes.
financials.loc[financials.sample(frac=0.03).index, 'ctd_pct_budget'] -= np.random.uniform(25.0, 50.0, int(NUM_TRANSACTIONS * 0.03))

# Anomaly 2: Extreme Financial Outliers & Negative Billing
financials.loc[financials.sample(frac=0.01).index, 'BilledAmount'] *= -1
financials.loc[financials.sample(frac=0.005).index, 'BilledAmount'] *= 100 

# Anomaly 3: Null Traps & Orphaned Records
logistics.loc[logistics.sample(frac=0.02).index, 'SiteID'] = np.nan
financials.loc[financials.sample(frac=0.01).index, 'LogisticsID'] = np.nan

# Anomaly 4: Date Formatting Corruption (Changing YYYY-MM-DD to DD/MM/YYYY)
corrupted_dates = logistics.sample(frac=0.02).index
logistics.loc[corrupted_dates, 'OrderDate'] = pd.to_datetime(logistics.loc[corrupted_dates, 'OrderDate']).dt.strftime('%d/%m/%Y')

# ---------------------------------------------------------
# 5. EXPORT TO SQLITE
# ---------------------------------------------------------
db_path = os.path.join(os.path.dirname(__file__), '../data/raw/legacy_erp.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

print(f"Exporting to SQLite database at: {db_path}")
conn = sqlite3.connect(db_path)

sites.to_sql('Sites', conn, index=False, if_exists='replace')
suppliers.to_sql('Suppliers', conn, index=False, if_exists='replace')
logistics.to_sql('Rental_Logistics', conn, index=False, if_exists='replace')
financials.to_sql('Project_Financials', conn, index=False, if_exists='replace')

conn.close()
print("Phase 1 Complete. Legacy database generated successfully.")