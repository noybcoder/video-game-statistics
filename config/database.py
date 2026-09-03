import psycopg2, duckdb, os, sys
from fastapi import Depends

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings

def connect_to_database_for_schema_creation(credentials) -> tuple :
    conn = psycopg2.connect(**credentials)
    conn.autocommit = True
    cur = conn.cursor()

    return conn, cur

def get_database_cursor():
    settings = Settings()

    try:
        _, cur = connect_to_database_for_schema_creation(settings.get_schema_creation_database_credentials)
        yield cur
    finally:
        close_connection_for_schema_creation

def connect_to_database_for_data_upload(db_config: dict, database: str='video_games') -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute('INSTALL POSTGRES;')
    conn.execute('LOAD POSTGRES;')

    conn.execute(f"ATTACH '{db_config}' AS {database} (TYPE postgres)")
    return conn

def close_connection_for_schema_creation(conn: psycopg2.extensions.connection, cur: psycopg2.extensions.cursor):
    cur.close()
    conn.close()