import psycopg2, duckdb
from psycopg2 import pool

connection_pool = None

def init_connection_pool(connection_string: str, minconn: int = 1, maxconn: int = 10):
    global connection_pool
    connection_pool = pool.SimpleConnectionPool(minconn, maxconn, connection_string)

def close_connection_pool():
    global connection_pool
    if connection_pool:
        connection_pool.closeall()

def connect_to_database_for_schema_creation(connection_string) -> tuple :
    conn = psycopg2.connect(connection_string)
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

def connect_to_database_for_data_upload(connection_string, database: str='supabase') -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute('INSTALL POSTGRES;')
    conn.execute('LOAD POSTGRES;')

    conn.execute(f"ATTACH '{connection_string}' AS {database} (TYPE postgres);")
    return conn

def close_connection_for_schema_creation(conn: psycopg2.extensions.connection, cur: psycopg2.extensions.cursor):
    cur.close()
    conn.close()