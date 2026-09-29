from prefect import flow, task
import os, sys, duckdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings
from config.paths import BRONZE_DIR, SILVER_DIR, CONFIG_DIR
from scripts.utils import get_table_structure
from scripts.extract import get_game_data, save_as_json
from scripts.transform import get_latest_file, create_core_tables, get_schema, get_table_metadata, process_junction_tables, save_as_parquet, save_table_names

settings = Settings()

@task
def extract(credentials: dict) -> None:
    for key, value in get_table_structure(CONFIG_DIR).items():
        data = get_game_data(
            fields=value['fields'], 
            credentials=credentials, 
            entity_name=key
        )
        save_as_json(data=data, entity_name=key)

@task
def transform() -> None:    
    conn = duckdb.connect()
    tables = []

    for entity in get_table_structure(CONFIG_DIR):
        file_path = get_latest_file(BRONZE_DIR, entity)
        create_core_tables(conn, entity, file_path)
        schema = get_schema(conn, entity)
        tables.append(get_table_metadata(conn, entity))

        process_junction_tables(conn, schema, entity, SILVER_DIR, tables)

        save_as_parquet(conn, entity, SILVER_DIR)
        save_table_names(CONFIG_DIR, tables)

@flow
def main() -> None:
    extract(settings.get_igdb_connection_credentials)
    transform()


if __name__ == '__main__':
    main.serve(
        name='my-first-deployment',
        cron="5 * * * *"
    )