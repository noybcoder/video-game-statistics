import psycopg2, duckdb

connection_pool = None

def init_connection_pool(credentials: dict, minconn: int = 1, maxconn: int = 10):
    global connection_pool
    connection_pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, **credentials)

def close_connection_pool():
    global connection_pool
    if connection_pool:
        connection_pool.closeall()

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