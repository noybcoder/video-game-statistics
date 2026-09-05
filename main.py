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

@app.get("/analytics/most_popular_genres_by_year")
async def genres_by_year(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        WITH genre_rank_by_year AS (
            SELECT
                ge.genre_name AS genre_name,
                ga.release_year AS release_year,
                ROUND(
                    (SUM(ga.total_rating * ga.total_rating_count) / NULLIF(SUM(ga.total_rating_count), 0))::NUMERIC, 2
                ) AS average_total_rating
            FROM games ga
            JOIN games_genres gg ON ga.game_id = gg.game_id
            JOIN genres ge ON gg.genre_id = ge.genre_id
            WHERE ga.total_rating_count >= 30
            GROUP BY ge.genre_name, ga.release_year
            HAVING COUNT(ga.game_id) >= 3
        )
        SELECT * FROM (
            SELECT   
                genre_name,
                release_year,
                average_total_rating,
                RANK() OVER(PARTITION BY release_year ORDER BY average_total_rating DESC) AS genre_rank
            FROM genre_rank_by_year
            ORDER BY release_year ASC, genre_rank ASC
        ) gr
        WHERE gr.genre_rank <= 10
    """)

    return cur.fetchall()

@app.get("/analytics/total_rating_by_genre")
async def total_rating_count_by_genre_distribution(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        SELECT
            release_year,
            ge.genre_name,
            PERCENTILE_CONT(ARRAY[0, 0.25, 0.5, 0.75, 1]) WITHIN GROUP (ORDER BY total_rating_count)
        FROM games ga
        JOIN games_genres gg ON ga.game_id = gg.game_id
        JOIN genres ge ON gg.genre_id = ge.genre_id
        WHERE ga.total_rating_count IS NOT NULL
        GROUP BY release_year, ge.genre_name
        ORDER BY release_year;
    """)

    return cur.fetchall()