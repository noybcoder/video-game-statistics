from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import *

app = FastAPI()



@app.get("/")
async def root():
    return [
        "What is the most popular genre?",
        "What genre does each developer/company specialize in?",
        "What game engines are most developers using?", 
        "What is the most popular game engine for each platform?",	
        "What is the most popular game engine for each genre?"
    ]

# @app.get("/games")
# async def all_games(cur=Depends(get_database_cursor)):
#     cur.execute("SELECT * FROM games;")
#     return cur.fetchone()

@app.get("/analytics/most_popular_genres_by_year")
async def genres_by_year(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        SELECT
            ge.genre_name,
            ga.release_year,
            SUM(total_rating * total_rating_count) / NULLIF(SUM(total_rating_count), 0) AS average_total_rating,
            MAX(total_rating) AS max_total_rating
        FROM games ga
        JOIN games_genres gg ON ga.game_id = gg.game_id
        JOIN genres ge ON gg.genre_id = ge.genre_id
        GROUP BY ge.genre_name, ga.release_year
        HAVING SUM(total_rating * total_rating_count) / NULLIF(SUM(total_rating_count), 0) IS NOT NULL
        ORDER BY ge.genre_name, ga.release_year;
    """)

    return cur.fetchall()

@app.get("/analytics/games_by_year")
async def games_by_year(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        SELECT
            release_year,
            COUNT(game_id)
        FROM games
        WHERE release_year <= 2026
        GROUP BY release_year;
    """)
    return cur.fetchall()

@app.get("/analytics/top_platforms_of_all_times")
async def games_by_platform(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        WITH games_per_platform AS (
            SELECT
                pl.platform_id AS platform_id,
                COUNT(ga.game_id) AS game_count
            FROM games ga
            JOIN games_platforms gp ON ga.game_id = gp.game_id
            JOIN platforms pl ON gp.platform_id = pl.platform_id
            WHERE ga.release_year <= 2026
            GROUP BY pl.platform_id
            ORDER BY game_count DESC
            LIMIT 15
        )
        SELECT
            pl.platform_name AS platform,
            COUNT(ga.game_id) AS game_count,
            ga.release_year AS release_year
        FROM games ga
        JOIN games_platforms gp ON ga.game_id = gp.game_id
        JOIN platforms pl ON gp.platform_id = pl.platform_id
        JOIN games_per_platform gpp ON pl.platform_id = gpp.platform_id
        WHERE ga.release_year <= 2026
        GROUP BY pl.platform_name, ga.release_year
        ORDER BY ga.release_year, pl.platform_name;
    """)
    return cur.fetchall()