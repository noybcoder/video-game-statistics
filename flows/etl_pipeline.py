from prefect import flow, task
import os, sys, duckdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings
from config.paths import R2_OBJECT_URL_PREFIX, BRONZE_DIR, SILVER_DIR, CONFIG_DIR
from scripts.extract import extract_pipelines
from scripts.transform import transform_pipelines
from scripts.load import load_pipelines

settings = Settings()
conn = duckdb.connect()

@task
def extract(r2_credentials: dict, igdb_credentials: dict, table_structure_dir: str, output_folder: str) -> None:
    extract_pipelines(r2_credentials, igdb_credentials, table_structure_dir, output_folder)

@task
def transform(
    conn: duckdb.DuckDBPyConnection, secret_credentials: str, client_credentials: dict,
    table_structure_dir: str, url_prefix: str, output_folder: str
)-> None:    
    transform_pipelines(conn, secret_credentials, client_credentials, table_structure_dir, url_prefix, output_folder)

@task
def load(
    connection_string: str, upload_conn: duckdb.DuckDBPyConnection, credentials: str, table_structure_dir: str, 
    url_prefix: str, output_folder: str, release_year: int=2010, rating: float=100.0
) -> None:
    load_pipelines(
        connection_string, upload_conn, credentials, table_structure_dir, 
        url_prefix, output_folder, release_year, rating
    )

@flow
def run_etl_pipeline() -> None:
    extract(settings.get_r2_client_credentials, settings.get_igdb_connection_credentials, CONFIG_DIR, BRONZE_DIR)
    transform(
        conn, settings.get_r2_secret_credentials, settings.get_r2_client_credentials, 
        CONFIG_DIR, R2_OBJECT_URL_PREFIX, SILVER_DIR
    )
    load(
        settings.get_database_connection_string, conn, settings.get_r2_secret_credentials, 
        CONFIG_DIR, R2_OBJECT_URL_PREFIX, SILVER_DIR
    )

if __name__ == '__main__':
    flow.from_source(
        source='https://github.com/noybcoder/video-game-statistics.git',
        entrypoint='flows/etl_pipeline.py:run_etl_pipeline',
    ).deploy(
        name='video-game-statistics-pipeline-deployment',
        work_pool_name='video-game-statistics-managed-pool',
        job_variables={
            "pip_packages": [
                "duckdb",
                "boto3",
                "psycopg2-binary",
                "pydantic-settings",
                "python-dotenv",
                "requests",
                "pycountry"
            ]
        },
        cron='* 5 * * *'
    )