from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import *

app = FastAPI()



@app.get("/")
async def root():
    return [
        "Top 20 games by rating (from highest to lowest) in each year",
        "Top 10 genres by rating (from highest to lowest) in each year",
        "Top 10 in each genre by rating (from highest to lowest) in each year",
        "Top 10/20 games engines by number of games developed (from highest to lowest) in each year",
        "Top 10/20 genres by number of games developed (from highest to lowest) in each year",
        "Top genre by video game developed by year (line chart)",
        "Top platform by video game developed by year (line chart)"
    ]

# @app.get("/games")
# async def all_games(cur=Depends(get_database_cursor)):
#     cur.execute("SELECT * FROM games;")
#     return cur.fetchone()

@app.get("/analytics/")
async def games_by_platform(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        WITH games_per_platform AS (
            SELECT
                pl.platform_name AS platform,
                COUNT(ga.game_id) AS game_count
            FROM games ga
            LEFT JOIN games_platforms gp
                ON ga.game_id = gp.game_id
            LEFT JOIN platforms pl
                ON gp.platform_id = pl.platform_id
            WHERE release_year <= 2026
            GROUP BY pl.platform_name
            ORDER BY game_count DESC
            LIMIT 15;
        )
        SELECT
            pl.platform_name AS platform,
            COUNT(ga.game_id) AS game_count
        FROM games ga
        LEFT JOIN games_platforms gp
            ON ga.game_id = gp.game_id
        LEFT JOIN platforms pl
            ON gp.platform_id = pl.platform_id
        WHERE release_year <= 2026
        GROUP BY pl.platform_name
        ORDER BY game_count DESC
        LIMIT 15; 
            
        
        
    """)
    return cur.fetchall()