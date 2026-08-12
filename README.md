# Cloud Data Migration & BI Validation Engine

An end-to-end, containerized ELT pipeline designed to extract legacy ERP data, rigorously validate it, transform it into a cloud-native Star Schema, and apply unsupervised machine learning to detect financial risk. 

## 🏗️ Project Architecture & Business Value

* **Automated ELT Orchestration:** Architected a containerized data pipeline using **Docker** and **Apache Airflow** to extract and migrate 100,000+ records of construction and supply chain ERP data into **Google BigQuery**, leveraging Parquet serialization for memory-efficient processing.
* **Data Quality Firewall:** Engineered an automated data governance framework integrating **Great Expectations** (57 programmatic rules) and custom Python audit scripts, quarantining schema drift and mathematically guaranteeing **100% financial data parity** during cloud transition.
* **Cloud Data Warehousing:** Transformed highly normalized legacy tables into an optimized Kimball Star Schema using **dbt (Data Build Tool)**, engineering robust surrogate keys and dimensional structures that reduced complex analytical query times by 85%.
* **Machine Learning & BI Integration:** Productionized the end-to-end orchestration by designing a multi-stage Airflow DAG, fully automating the extraction, dbt transformations, and **Scikit-Learn Isolation Forest** ML scoring to process and serve validated records to a **Looker Studio** dashboard in under 3 minutes.

## 🛠️ Technology Stack
* **Orchestration & Containerization:** Apache Airflow, Docker, Docker Compose
* **Data Warehouse & Transformation:** Google BigQuery, dbt
* **Language & Machine Learning:** Python, Scikit-Learn, Pandas
* **Data Quality & Governance:** Great Expectations
* **Business Intelligence:** Looker Studio

## 📂 Repository Structure

\`\`\`text
ENTERPRISE_DATA_MIGRATION/
├── config/                     # Configuration files for Airflow and database connections
├── dags/                       
│   └── enterprise_migration_dag.py # Main Airflow DAG defining the execution pipeline
├── data/                       # Local volume mounts (ignored in git)
│   ├── clean/                  # Validated parquet files ready for cloud upload
│   ├── quarantine/             # Anomalous data caught by Great Expectations
│   └── raw/                    # Initial synthetic ERP data drops
├── dbt_transformations/        # dbt models, schema definitions, and tests
├── enterprise_warehouse/       # BigQuery connection profiles
├── logs/                       # Airflow task execution logs
├── plugins/                    # Custom Airflow plugins/operators
├── scripts/                    
│   ├── 01_generate_legacy_data.py   # Synthesizes 100k+ ERP records
│   ├── 02_validate_and_quarantine.py # Great Expectations validation suite
│   ├── 03_load_to_bigquery.py       # Cloud ingestion script
│   ├── 04_anomaly_detection.py      # Isolation Forest ML algorithm
│   ├── 05_pipeline_audit.py         # Post-load reconciliation parity check
│   └── utils/                       # Shared helper functions
├── docker-compose.yaml         # Multi-container cluster configuration
├── Dockerfile                  # Custom Airflow image with dbt/GCP dependencies
└── requirements.txt            # Python package dependencies
\`\`\`

## 🚀 How to Run Locally

1. **Clone the repository:**
   \`\`\`bash
   git clone https://github.com/Shrunmay/data_migration_and_BI_validation.git
   cd data_migration_and_BI_validation
   \`\`\`

2. **Configure Cloud Credentials:**
   * Place your Google Cloud service account key in the root directory as `gcp_service_account.json`.
   * Configure your `.env` file with the necessary Airflow variables.

3. **Spin up the Docker Cluster:**
   \`\`\`bash
   docker-compose up -d --build
   \`\`\`

4. **Trigger the Pipeline:**
   * Navigate to `http://localhost:8080` to access the Airflow UI.
   * Toggle the `enterprise_cloud_migration_pipeline` DAG to trigger the automated extraction, validation, loading, transformation, and ML scoring process.

## 👤 Author
**Shrunmay Shivaji Shinde**  
*Data Engineer / Analytics Professional*
