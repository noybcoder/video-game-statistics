import duckdb, os, re, sys, functools, pycountry, inspect, json
from utils import *
from typing import Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

####### Core Functions  #######
def create_direct_link_table(func):
    @functools.wraps(func)
    def wrappper_add_query(conn: duckdb.DuckDBPyConnection, entity_name: str, path: str):
        try:
            param = func(conn) if 'conn' in inspect.signature(func).parameters else func()

            conn.execute(f"""
                CREATE OR REPLACE TABLE {entity_name} AS 
                    SELECT
                        CAST(d.data ->> 'id' AS INTEGER) AS {get_singular_entity_name(entity_name)}_id,
                        d.data ->> 'name' AS {get_singular_entity_name(entity_name)}_name,
                        {param}
                    FROM read_json($path, maximum_object_size=60000000) AS g
                    CROSS JOIN UNNEST(g.data) AS d(data) 
            """, {'path': path})

            return conn.table(entity_name)
        except duckdb.ParserException as e:
            print(f'Error: {e}')
    return wrappper_add_query

def create_junction_table(conn: duckdb.DuckDBPyConnection, first_primary_key: str, second_primary_key: str):
    table_name = get_junction_table_name(first_primary_key, second_primary_key)
    renamed_second_primary_key = 'games' if re.match(r'^(develop|publish)ed$', second_primary_key) else second_primary_key
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
            SELECT 
                {get_singular_entity_name(first_primary_key)}_id, 
                UNNEST({second_primary_key}) AS {get_singular_entity_name(renamed_second_primary_key)}_id
            FROM {first_primary_key}
    """)

    return conn.table(table_name)

@create_direct_link_table
def create_game_table():
    return f"""
        TO_TIMESTAMP(CAST(d.data ->> 'first_release_date' AS BIGINT))::DATE AS first_release_date,
        YEAR(first_release_date) AS release_year,
        CAST(d.data ->> 'genres' AS INTEGER[]) AS genres,
        CAST(d.data ->> 'game_engines' AS INTEGER[]) AS game_engines,
        CAST(d.data ->> 'platforms' AS INTEGER[]) AS platforms,
        CAST(d.data ->> 'game_type' AS INTEGER) AS game_type,
        CAST(d.data ->> 'rating' AS DECIMAL(5, 2)) AS rating,
        CAST(d.data ->> 'rating_count' AS INTEGER) AS rating_count,
        CAST(d.data ->> 'total_rating' AS DECIMAL(5, 2)) AS total_rating,
        CAST(d.data ->> 'total_rating_count' AS INTEGER) AS total_rating_count,
        CAST(d.data ->> 'aggregated_rating' AS DECIMAL(5, 2)) AS aggregated_rating,
        CAST(d.data ->> 'aggregated_rating_count' AS INTEGER) AS aggregated_rating_count
    """

@create_direct_link_table
def create_company_table(conn: duckdb.DuckDBPyConnection) -> str:
    conn.create_function("get_country_name", get_country_name, ["INTEGER"], "VARCHAR")

    return f"""
        CAST(d.data ->> 'developed' AS INTEGER[]) AS developed,
        CAST(d.data ->> 'published' AS INTEGER[]) AS published,
        get_country_name(CAST(d.data ->> 'country' AS INTEGER)) AS country
    """

def remove_fields(conn: duckdb.DuckDBPyConnection, entity_name: str, *fields):
    for field in fields:
        conn.execute(f'ALTER TABLE {entity_name} DROP {field}')
    return conn.table(entity_name)

@create_direct_link_table
def create_generic_table():
    return ''

def create_core_tables(conn, entity, file_path):
    if entity == 'games':
        table = create_game_table(conn, entity, file_path)
    elif entity == 'companies':
        table = create_company_table(conn, entity, file_path)
    else:
        table = create_generic_table(conn, entity, file_path)

    return table

###### Help Functions ######
def get_junction_table_name(primary_entity, secondary_entity):
    return f'{primary_entity}_{secondary_entity}'

def get_latest_file(file_path: str, entity_name: str) -> str:
    try:
        files = [os.path.join(file_path, file) for file in os.listdir(file_path) if re.match(f'{entity_name}_raw.*json', file)]
        return max(files, key=os.path.getctime)
    except ValueError as e:
        print(f'Error: ${e}')

def get_country_name(country_code: int) -> Union[str, None]:
    try:
        country = pycountry.countries.get(numeric=str(country_code).zfill(3))
        return country.name
    except(AttributeError):
        print(f'The country code "{country_code}" is not valid.')
        return None

def save_as_parquet(conn, entity_name, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    conn.execute(f"""
        COPY {entity_name} TO '{output_folder}/{entity_name}.parquet' (FORMAT parquet)
    """)

def save_table_names(output_folder, content, file_name: str='entity_names.json'):
    os.makedirs(output_folder, exist_ok=True)
    file_name = os.path.join(output_folder, file_name)

    with open(file_name, 'w') as f:
        json.dump(content, f, indent=2)

def get_schema(conn: duckdb.DuckDBPyConnection, entity_name: str):
    try:
        return {row[0]: row[1] for row in conn.execute(f'DESCRIBE {entity_name}').fetchall()}
    except duckdb.CatalogException as e:
        print(f'Error: {e}')
    except TypeError as e:
        print(f'Error: {e}')

def get_primary_keys(conn: duckdb.DuckDBPyConnection, entity_name: str):
    try:
        return [row[0] for row in conn.execute(f'DESCRIBE {entity_name}').fetchall() if re.match(r'\w+_id$', row[0])]
    except duckdb.CatalogException as e:
        print(f'Error: {e}')
    except TypeError as e:
        print(f'Error: {e}')

def get_table_metadata(conn, primary_entity, secondary_entity=None, original_primary_entity=None):
    primary_keys = get_primary_keys(conn, primary_entity)

    details = {
        'entity': primary_entity,
        'primary_keys': primary_keys,
        'type': 'junction' if len(primary_keys) > 1 else 'direct_link' 
    }

    if len(primary_keys) > 1:
        details['parent_tables'] = [secondary_entity, original_primary_entity]
        if re.match(r'.+(develop|publish)ed$', primary_entity):
            details['parent_tables'] = [secondary_entity, 'games']


    return details

if __name__ == '__main__':
    conn = duckdb.connect()
    BRONZE_DIR = os.path.join(os.getcwd(), 'data/bronze')
    SILVER_DIR = os.path.join(os.getcwd(), 'data/silver')
    CONFIG_DIR = os.path.join(os.getcwd(), 'config')

    tables = []

    for entity in get_table_structure(CONFIG_DIR):
        file_path = get_latest_file(BRONZE_DIR, entity)
        core_table = create_core_tables(conn, entity, file_path)
        schema = get_schema(conn, entity)
        tables.append(get_table_metadata(conn, entity))

        for field in schema:
            if schema[field] == 'INTEGER[]':
                create_junction_table(conn, entity, field)
                junction_table_name = get_junction_table_name(entity, field)
                core_table = remove_fields(conn, entity, field)
                save_as_parquet(conn, junction_table_name, SILVER_DIR)
                tables.append(get_table_metadata(conn, junction_table_name, entity, field))

        save_as_parquet(conn, entity, SILVER_DIR)
        save_table_names(CONFIG_DIR, tables)