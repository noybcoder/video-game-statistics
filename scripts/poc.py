import duckdb, os
import numpy as np
import inflect

path = os.path.join(os.getcwd(), 'data/landing/genres_raw_2026-08-14_14-54-52.json')
conn = duckdb.connect()

entity_name = 'genres'

# conn.execute(f"""
#     CREATE OR REPLACE TABLE {entity_name} AS
#         SELECT
#             CAST(d.data ->> 'id' AS INTEGER) AS id,
#             d.data ->> 'name' AS name,
#             CAST(d.data ->> 'developed' AS INTEGER[]) as developed,
#             CAST(d.data ->> 'published' AS INTEGER[]) as published 
#         FROM read_json($path, maximum_object_size=60000000) AS c
#         CROSS JOIN UNNEST(c.data) AS d(data)
# """, {'path': path})

# conn.execute(f"""
#     CREATE OR REPLACE TABLE {entity_name} AS
#         SELECT
#             CAST(d.data ->> 'id' AS INTEGER) AS id,
#             d.data ->> 'name' AS name,
#             TO_TIMESTAMP(CAST(d.data ->> 'first_release_date' AS BIGINT))::DATE AS release_date,
#             YEAR(release_date) AS release_year,
#             CAST(d.data ->> 'genres' AS INTEGER[]) AS genres,
#             CAST(d.data ->> 'game_engines' AS INTEGER[]) AS game_engines,
#             CAST(d.data ->> 'platforms' AS INTEGER[]) AS platforms,
#             CAST(d.data ->> 'game_type' AS INTEGER) AS game_type,
#             CAST(d.data ->> 'rating' AS FLOAT) AS rating,
#             CAST(d.data ->> 'rating_count' AS INTEGER) AS rating_count,
#             CAST(d.data ->> 'total_rating' AS FLOAT) AS total_rating,
#             CAST(d.data ->> 'total_rating_count' AS INTEGER) AS total_rating_count,
#             CAST(d.data ->> 'aggregated_rating' AS FLOAT) AS aggregated_rating,
#             CAST(d.data ->> 'aggregated_rating_count' AS INTEGER) AS aggregated_rating_count
#         FROM read_json($path, maximum_object_size=60000000) AS g
#         CROSS JOIN UNNEST(g.data) AS d(data)
# """, {'path': path})

# conn.execute(f"""
#     CREATE OR REPLACE TABLE games_genres AS
#         SELECT id, UNNEST(genres) FROM games
# """)

# conn.execute(f"""
#     CREATE OR REPLACE TABLE games_game_engines AS
#         SELECT id, UNNEST(game_engines) FROM games
# """)

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

def create_direct_link_table(conn, entity_name):
    conn.execute(f"""
        CREATE OR REPLACE TABLE {entity_name} AS 
            SELECT
                CAST(d.data ->> 'id' AS INTEGER) AS id,
                d.data ->> 'name' AS name
            FROM read_json($path, maximum_object_size=60000000) AS g
            CROSS JOIN UNNEST(g.data) AS d(data)
    """, {'path': path})

    return conn.table(entity_name)

create_direct_link_table(conn, entity_name).show()


# create_junction_table(conn, first_primary_key, second_primary_key).show()


# conn.sql("""
#     SELECT table_name, column_name
#     FROM duckdb_columns()
#     WHERE data_type LIKE '%[]'
# """).show()
