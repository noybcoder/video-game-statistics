import duckdb, os
import numpy as np
import inflect, functools, pycountry, inspect

path = os.path.join(os.getcwd(), 'data/landing/companies_raw_2026-08-19_09-21-15.json')
conn = duckdb.connect()

entity_name = 'companies'

first_primary_key = 'companies'
second_primary_key = 'published'

def create_junction_table(conn, first_primary_key: str, second_primary_key: str):
    table_name = f'{first_primary_key}_{second_primary_key}'
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
            SELECT 
                id AS {get_singular_entity_name(first_primary_key)}, 
                UNNEST({second_primary_key}) AS {get_singular_entity_name(second_primary_key)}
            FROM {first_primary_key}
    """)

    return conn.table(table_name)

def get_singular_entity_name(attribute: str) -> str:
    p = inflect.engine()
    singular = p.singular_noun(attribute)
    if singular:
        return f'{singular}_id'
    return f'{attribute}_id'
    
def create_direct_link_table(func):
    @functools.wraps(func)
    def wrappper_add_query(conn, entity_name: str, path: str):

        param = func(conn) if 'conn' in inspect.signature(func).parameters else func()

        conn.execute(f"""
            CREATE OR REPLACE TABLE {entity_name} AS 
                SELECT
                    CAST(d.data ->> 'id' AS INTEGER) AS id,
                    d.data ->> 'name' AS name,
                    {param}
                FROM read_json($path, maximum_object_size=60000000) AS g
                CROSS JOIN UNNEST(g.data) AS d(data) 
        """, {'path': path})

        return conn.table(entity_name)
    return wrappper_add_query

@create_direct_link_table
def create_game_table():
    return f"""
        TO_TIMESTAMP(CAST(d.data ->> 'first_release_date' AS BIGINT))::DATE AS release_date,
        YEAR(release_date) AS release_year,
        CAST(d.data ->> 'genres' AS INTEGER[]) AS genres,
        CAST(d.data ->> 'game_engines' AS INTEGER[]) AS game_engines,
        CAST(d.data ->> 'platforms' AS INTEGER[]) AS platforms,
        CAST(d.data ->> 'game_type' AS INTEGER) AS game_type,
        CAST(d.data ->> 'rating' AS FLOAT) AS rating,
        CAST(d.data ->> 'rating_count' AS INTEGER) AS rating_count,
        CAST(d.data ->> 'total_rating' AS FLOAT) AS total_rating,
        CAST(d.data ->> 'total_rating_count' AS INTEGER) AS total_rating_count,
        CAST(d.data ->> 'aggregated_rating' AS FLOAT) AS aggregated_rating,
        CAST(d.data ->> 'aggregated_rating_count' AS INTEGER) AS aggregated_rating_count
    """

@create_direct_link_table
def create_company_table(conn):
    conn.create_function("get_country_name", get_country_name, ["INTEGER"], "VARCHAR")

    return f"""
        CAST(d.data ->> 'developed' AS INTEGER[]) AS game_developed,
        CAST(d.data ->> 'published' AS INTEGER[]) AS game_published,
        CAST(d.data ->> 'country' AS INTEGER) AS country_code,
        get_country_name(country_code) AS country
    """

@create_direct_link_table
def create_generic_table():
    return ''

def get_country_name(country_code: int) -> str | None:
    try:
        country = pycountry.countries.get(numeric=str(country_code).zfill(3))
        return country.name
    except(AttributeError):
        print(f'The country code "{country_code}" is not valid.')
        return None

add_generic_data = create_company_table(conn, entity_name, path)
add_generic_data.show()