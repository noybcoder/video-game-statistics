import duckdb, os

path = os.path.join(os.getcwd(), 'data/landing/games_raw_2026-08-14_14-54-44.json')
conn = duckdb.connect()

entity_name = 'games'

conn.execute(f"""
    CREATE OR REPLACE TABLE {entity_name} AS
        SELECT
            CAST(d.data ->> 'id' AS INTEGER) AS id,
            d.data ->> 'name' AS name,
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
        FROM read_json($path, maximum_object_size=60000000) AS r
        CROSS JOIN UNNEST(r.data) AS d(data)
""", {'path': path})

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

conn.sql("""
    SELECT table_name, column_name
    FROM duckdb_columns()
    WHERE data_type LIKE '%[]'
""").show()