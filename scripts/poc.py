import duckdb, os

path = os.path.join(os.getcwd(), 'data/landing/games_raw_2026-08-14_14-54-44.json')
conn = duckdb.connect()

conn.execute("""
    CREATE OR REPLACE TABLE games AS
        SELECT * FROM read_json($path, maximum_object_size=60000000)
""", {'path': path})

conn.sql("""
    SELECT * FROM games
""").show()