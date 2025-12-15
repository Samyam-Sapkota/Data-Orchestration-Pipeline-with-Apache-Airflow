# dags/etl_postgres_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from etl.extract import DarazScraperStrict
from etl.transform import clean_laptop_data
from etl.load import load_to_postgres

# Configuration
POSTGRES_CONN_ID = "postgres_default"
TABLE_NAME = "products"
DAGS_FOLDER = Path(__file__).parent
RAW_DATA_PATH = DAGS_FOLDER / "raw" / "rawdata.csv"
CLEAN_DATA_PATH = DAGS_FOLDER / "clean" / "cleaned.csv"

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def extract_data(**context):
    """Extract data from Daraz and save to raw folder"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    # Ensure raw directory exists
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )
    
    try:
        # Scrape data
        scraper = DarazScraperStrict(driver)
        data = scraper.scrape("laptop",2)
        
        # Save raw data to CSV
        df = pd.DataFrame(data)
        df.to_csv(RAW_DATA_PATH, encoding="utf-8-sig", index=False)
        
        print(f"✅ Extracted {len(df)} records and saved to {RAW_DATA_PATH}")
        
        # Push metadata to XCom
        context['ti'].xcom_push(key='raw_records_count', value=len(df))
        
    finally:
        driver.quit()


def transform_data(**context):
    """Transform raw data and save to clean folder"""
    # Ensure clean directory exists
    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Read raw data
    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"📂 Loaded {len(df_raw)} raw records from {RAW_DATA_PATH}")
    
    # Clean the data
    df_clean = clean_laptop_data(df_raw)
    
    # Save cleaned data
    df_clean.to_csv(CLEAN_DATA_PATH, encoding="utf-8-sig", index=False)
    
    print(f"✅ Transformed and saved {len(df_clean)} cleaned records to {CLEAN_DATA_PATH}")
    
    # Push metadata to XCom
    context['ti'].xcom_push(key='clean_records_count', value=len(df_clean))


def load_data(**context):
    """Load cleaned data to PostgreSQL"""
    # Read cleaned data
    df_clean = pd.read_csv(CLEAN_DATA_PATH)
    print(f"📂 Loaded {len(df_clean)} cleaned records from {CLEAN_DATA_PATH}")
    
    # Load to PostgreSQL
    load_to_postgres(
        df=df_clean,
        table_name=TABLE_NAME,
        postgres_conn_id=POSTGRES_CONN_ID
    )
    
    print(f"✅ Loaded {len(df_clean)} records to PostgreSQL table '{TABLE_NAME}'")


# Define the DAG
with DAG(
    dag_id="Daraz_ETL_dag",
    default_args=default_args,
    description="ETL pipeline to scrape Daraz laptop data and load to PostgreSQL",
   # schedule="0 2 * * *",  # Run daily at 2 AM
    schedule = None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "postgres", "daraz", "scraping"],
    max_active_runs=1,  # Prevent concurrent runs
) as dag:
    
    # Task 1: Extract data from Daraz
    extract_task = PythonOperator(
        task_id="extract_from_daraz",
        python_callable=extract_data,
    )
    
    # Task 2: Transform/clean the data
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )
    
    # Task 3: Load data to PostgreSQL
    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_data,
    )
    
    # Task 4: Validate count in PostgreSQL
    validate_data_counts = SQLExecuteQueryOperator(
        task_id="validate_data_counts",
        conn_id=POSTGRES_CONN_ID,
        sql=f"""
            SELECT json_build_object(
                'total_records', COUNT(*),
                'unique_records', COUNT(DISTINCT product_id)
            )
            FROM {TABLE_NAME};
        """,
)

    # Define task dependencies
    extract_task >> transform_task >> load_task >> validate_data_counts
