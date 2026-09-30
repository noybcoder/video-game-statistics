from prefect import flow, task
import os, sys, duckdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings
from config.paths import BRONZE_DIR, SILVER_DIR, CONFIG_DIR
from scripts.extract import extract_all_tables
from scripts.transform import transform_all_tables
from scripts.load import load_pipelines

settings = Settings()

@task
def extract(credentials: dict, table_structure_dir: str, output_folder: str) -> None:
    extract_all_tables(credentials, table_structure_dir, output_folder)

@task
def transform(table_structure_dir: str, source_dir: str, output_folder: str) -> None:    
    conn = duckdb.connect()
    transform_all_tables(conn, table_structure_dir, source_dir, output_folder)

@task
def load(connection_string: str, table_structure_dir: str, release_year: int=2010, rating: float=100.0) -> None:
    load_pipelines(connection_string, table_structure_dir, release_year, rating)

@flow
def run_etl_pipeline() -> None:
    extract(settings.get_igdb_connection_credentials, CONFIG_DIR, BRONZE_DIR)
    transform(CONFIG_DIR, BRONZE_DIR, SILVER_DIR)
    load(settings.get_database_connection_string, CONFIG_DIR)

if __name__ == '__main__':
    flow.from_source(
        source='https://github.com/noybcoder/video-game-statistics.git',
        entrypoint='flows/etl_pipeline.py:run_etl_pipeline',
    ).deploy(
        name='video-game-statistics-pipeline-deployment',
        work_pool_name='video-game-statistics-managed-pool',
        cron='* 5 * * *'
    )