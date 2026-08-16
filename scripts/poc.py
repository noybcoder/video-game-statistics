import duckdb, os
import numpy as np

path = os.path.join(os.getcwd(), 'data/landing/companies_raw_2026-08-14_14-56-18.json')
conn = duckdb.connect()

entity_name = 'games'

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

# conn.execute(f"""
#     CREATE OR REPLACE TABLE games_platforms AS
#         SELECT id, UNNEST(platforms) FROM games
# """)

conn.execute(f"""
    CREATE OR REPLACE TABLE companies AS 
        SELECT
            CAST(d.data ->> 'id' AS INTEGER) AS id,
            d.data ->> 'name' AS name,
            CAST(d.data ->> 'developed' AS INTEGER[]) AS developed,
            CAST(d.data ->> 'published' AS INTEGER[]) AS published
        FROM read_json($path, maximum_object_size=60000000) AS c
        CROSS JOIN UNNEST(c.data) AS d(data)
""", {'path': path})

conn.sql(f"""
    SELECT * FROM companies
""").show()

conn.sql("""
    SELECT table_name, column_name
    FROM duckdb_columns()
    WHERE data_type LIKE '%[]' AND (table_name = 'games' OR table_name = 'companies')
""").show()