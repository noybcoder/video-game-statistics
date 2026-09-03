import psycopg2, duckdb, os, sys
from fastapi import Depends
from psycopg2 import pool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings

settings = Settings()

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10, **settings.get_schema_creation_database_credentials
)

def connect_to_database_for_schema_creation(credentials) -> tuple :
    conn = psycopg2.connect(**credentials)
    conn.autocommit = True
    cur = conn.cursor()

    return conn, cur

def get_database_cursor():
    conn = connection_pool.getconn()
    cur = conn.cursor()

    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        connection_pool.putconn(conn)

def connect_to_database_for_data_upload(db_config: dict, database: str='video_games') -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute('INSTALL POSTGRES;')
    conn.execute('LOAD POSTGRES;')

    conn.execute(f"ATTACH '{db_config}' AS {database} (TYPE postgres)")
    return conn

def close_connection_for_schema_creation(conn: psycopg2.extensions.connection, cur: psycopg2.extensions.cursor):
    cur.close()
    conn.close()