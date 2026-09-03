from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import *

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/games")
async def all_games(cur=Depends(get_database_cursor)):
    cur.execute("SELECT * FROM games;")
    return cur.fetchone()

@app.get("/analytics/games_by_year")
async def games_by_year(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        SELECT
            COUNT(game_id),
            release_year
        FROM games
        WHERE release_year <= 2026
        GROUP BY release_year;
    """)
    return cur.fetchall()