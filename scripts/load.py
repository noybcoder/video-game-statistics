import psycopg2, duckdb, os, functools, inspect, sys
from dotenv import load_dotenv
from utils import *

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from config.paths import CONFIG_DIR

def connect_to_database_for_data_upload(db_config: dict, database: str='video_games') -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute('INSTALL POSTGRES;')
    conn.execute('LOAD POSTGRES;')

    conn.execute(f"ATTACH '{db_config}' AS {database} (TYPE postgres)")
    return conn

def get_data_file(entity_name: str, path: str='data/silver') -> str:
    return os.path.join(os.getcwd(), f'{path}/{entity_name}.parquet')

def create_direct_link_schema(func) -> None:
    @functools.wraps(func)
    def wrapper_add_query(cur: psycopg2.extensions.cursor, entity_name: str, *args) -> None:
        fields = func(*args) if inspect.signature(func).parameters else func()

        cur.execute(f"""
            DROP TABLE IF EXISTS {entity_name} CASCADE;

            CREATE TABLE {entity_name} (
                {get_singular_entity_name(entity_name)}_id INTEGER PRIMARY KEY,
                {get_singular_entity_name(entity_name)}_name VARCHAR(255) NOT NULL
                {fields}
            );
        """)
    return wrapper_add_query

@create_direct_link_schema
def create_games_schema(release_year: int, rating: float) -> str:
    return  f"""
                ,
                first_release_date DATE,
                release_year INTEGER CHECK (release_year >= {release_year}),
                game_type INTEGER,
                rating REAL CHECK (rating <= {rating}),
                rating_count INTEGER,
                total_rating REAL CHECK (total_rating <= {rating}),
                total_rating_count INTEGER,
                aggregated_rating REAL CHECK (aggregated_rating <= {rating}),
                aggregated_rating_count INTEGER
            """

@create_direct_link_schema
def create_companies_schema() -> str:
    return  f"""
        ,
        country VARCHAR(255)
    """

@create_direct_link_schema
def create_regular_schema() -> str:
    return  '';

def create_core_schema(cur: psycopg2.extensions.cursor, table_config: list, release_year: int, rating: float) -> None:
    if table_config['entity'] == 'games':
        create_games_schema(cur, table_config['entity'], release_year, rating)
    elif table['entity'] == 'companies':
        create_companies_schema(cur, table_config['entity'])
    else:
        create_regular_schema(cur, table_config['entity'])

def create_junction_schema(cur: psycopg2.extensions.cursor, table_config: list):
    entity_name = table_config['entity']
    first_primary_key, second_primary_key = table_config['primary_keys']
    first_parent_table, second_parent_table = table_config['parent_tables']

    cur.execute(f"""
        DROP TABLE IF EXISTS {entity_name};

        CREATE TABLE {entity_name} (
            {first_primary_key} INTEGER,
            {second_primary_key} INTEGER,
            PRIMARY KEY ({first_primary_key}, {second_primary_key}),
            CONSTRAINT fk_{first_primary_key} 
                FOREIGN KEY ({first_primary_key}) REFERENCES {first_parent_table}({first_primary_key}) ON DELETE CASCADE,
            CONSTRAINT fk_{second_primary_key} 
                FOREIGN KEY ({second_primary_key}) REFERENCES {second_parent_table}({second_primary_key}) ON DELETE CASCADE
        );
    """)

def load_data_to_direct_link_table(conn: duckdb.DuckDBPyConnection, entity_name: str, path: str, database: str='video_games'):
    conn.execute(f"""
        INSERT INTO {database}.{entity_name}
        SELECT * FROM read_parquet($path)
    """, {'path': path})

def load_data_to_junction_table(conn: duckdb.DuckDBPyConnection, table_config: list, path: str, database: str='video_games'):
    entity_name = table_config['entity']
    first_primary_key, second_primary_key = table_config['primary_keys']
    first_parent_table, second_parent_table = table_config['parent_tables']

    conn.execute(f"""
        INSERT INTO {database}.{entity_name}
        SELECT 
            a.{first_primary_key},
            a.{second_primary_key}
        FROM read_parquet($path) AS a
        INNER JOIN {database}.{first_parent_table} AS b
            ON a.{first_primary_key} = b.{first_primary_key}
        INNER JOIN {database}.{second_parent_table} AS c
            ON a.{second_primary_key} = c.{second_primary_key}
    """, {'path': path})

def connect_to_database_for_schema_creation(credentials) -> tuple :
    conn = psycopg2.connect(**credentials)
    conn.autocommit = True
    cur = conn.cursor()

    return conn, cur

def close_connection_for_schema_creation(conn: psycopg2.extensions.connection, cur: psycopg2.extensions.cursor):

    cur.close()
    conn.close()

if __name__ == '__main__':
    settings = Settings()

    schema_conn, cur = connect_to_database_for_schema_creation(settings.get_schema_creation_database_credentials)
    upload_conn = connect_to_database_for_data_upload(settings.get_data_load_database_credentials)

    tables = sorted(get_table_structure(CONFIG_DIR, 'entity_names.json'), key=lambda x: x['type'])

    for table in tables:
        path = os.path.join(os.getcwd(), f"data/silver/{table['entity']}.parquet")

        print(f"Creating schema for {table['entity']}")
        if table['type'] == 'direct_link':
            create_core_schema(cur, table, 2010, 100.0)
            load_data_to_direct_link_table(upload_conn, table['entity'], path)
        else:
            create_junction_schema(cur, table)
            load_data_to_junction_table(upload_conn, table, path)

    close_connection_for_schema_creation(schema_conn, cur)
