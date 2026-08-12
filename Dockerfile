FROM apache/airflow:2.8.1-python3.11

# Switch to root to install system dependencies if needed (optional, keeping it light)
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user to install Python packages
USER airflow

# Install all the dependencies we used in our local virtual environment
RUN pip install --no-cache-dir \
    pandas==2.2.0 \
    numpy==1.26.4 \
    faker==22.6.0 \
    great_expectations==0.18.12 \
    pyarrow==15.0.0 \
    google-cloud-bigquery==3.17.2 \
    dbt-bigquery==1.7.3 \
    scikit-learn==1.4.0 \
    db-dtypes==1.2.0