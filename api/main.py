from fastapi import FastAPI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import *

app = FastAPI()



@app.get("/")
async def root():
    return [
        "What is the most popular genre?", # Heat map
        "What genre does each developer/company specialize in?", # A matrix or table
        "What game engines are most developers using?", # A bar chart
        "What is the most popular game engine for each platform?",	
        "What is the most popular game engine for each genre?"
    ]

@app.get("/analytics/most_popular_platforms_by_year")
def genres_by_year(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        With most_popular_platforms AS (
            SELECT
                gp.platform_id,
                pl.platform_name,
                COUNT(DISTINCT ga.game_id) AS game_count
            FROM games_platforms gp
            JOIN games ga ON gp.game_id = ga.game_id
            JOIN platforms pl ON gp.platform_id = pl.platform_id
            WHERE ga.release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15 AND ga.total_rating_count >= 30
            GROUP BY gp.platform_id, pl.platform_name
            ORDER BY game_count DESC
            LIMIT 15
        )
        SELECT
            mpp.platform_name,
            ga.release_year,
            COUNT(DISTINCT ga.game_id)
        FROM most_popular_platforms mpp
        JOIN games_platforms gp ON mpp.platform_id = gp.platform_id
        JOIN games ga ON gp.game_id = ga.game_id
        WHERE ga.release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15 AND ga.total_rating_count >= 30
        GROUP BY mpp.platform_name, ga.release_year
        ORDER BY mpp.platform_name ASC, ga.release_year ASC, COUNT(DISTINCT ga.game_id) DESC
    """)

    return [{'platform': result[0], 'release_year': result[1], 'game_count': result[2]} for result in cur.fetchall()]

# A pie chart
@app.get("/analytics/genre_distribution")
async def genre_by_market_share(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        SELECT 
            ge.genre_name,
            COUNT(DISTINCT gg.game_id)
        FROM games_genres gg
        JOIN genres ge ON gg.genre_id = ge.genre_id
        JOIN games ga ON gg.game_id = ga.game_id
        WHERE release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15 AND total_rating_count >= 30
        GROUP BY ge.genre_name
    """)

    return [{'genre': result[0], 'game_count': result[1]} for result in cur.fetchall()]

# A matrix or table
@app.get("/analytics/genres_per_developer")
async def game_genres_by_developer(cur=Depends(get_database_cursor)):
    cur.execute(f"""
        With active_developers AS (
            SELECT
                cd.company_id AS company_id,
                COUNT(cd.game_id) AS total_game_count
            FROM companies_developed cd
            JOIN games ga ON cd.game_id = ga.game_id
            WHERE ga.total_rating_count >= 30 AND ga.release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15
            GROUP BY cd.company_id
            HAVING MAX(ga.release_year) >= EXTRACT(YEAR FROM CURRENT_DATE) - 3 AND COUNT(DISTINCT ga.game_id) >= 5
        ),
        developer_genre_distribution AS (
            SELECT
                co.company_name AS developer,
                ge.genre_name AS genre,
                COUNT(DISTINCT cd.game_id) AS game_count_by_genre,
                ROUND(100.0 * COUNT(DISTINCT cd.game_id) / ad.total_game_count, 1) AS pct_of_developer_output
            FROM active_developers ad
            JOIN companies_developed cd ON ad.company_id = cd.company_id
            JOIN companies co ON cd.company_id = co.company_id
            JOIN games ga ON cd.game_id = ga.game_id
            JOIN games_genres gg ON ga.game_id = gg.game_id
            JOIN genres ge ON gg.genre_id = ge.genre_id
            WHERE ga.total_rating_count >= 30
            GROUP BY co.company_name, ge.genre_name, ad.total_game_count
        )
        SELECT
            developer,
            genre,
            game_count_by_genre,
            pct_of_developer_output
        FROM (
            SELECT
                *,
                RANK() OVER(PARTITION BY developer ORDER BY pct_of_developer_output DESC) AS genre_rank
            FROM developer_genre_distribution
        ) final
        WHERE final.genre_rank = 1;
        
        
    """)

    return [{'developer': result[0], 'genre': result[1], 'total_game_count': result[2], 'pct_of_total_game_count': result[3]} for result in cur.fetchall()]

# A bar chart?
@app.get("/analytics/top_n_game_engines/{top_n}")
async def game_engine_by_developer(top_n: int= 10, cur=Depends(get_database_cursor)):
    cur.execute(f"""
        With active_developers AS (
            SELECT
                cd.company_id AS company_id
            FROM companies_developed cd
            JOIN games ga ON cd.game_id = ga.game_id
            WHERE ga.total_rating_count >= 30 AND ga.release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15
            GROUP BY cd.company_id
            HAVING MAX(ga.release_year) >= EXTRACT(YEAR FROM CURRENT_DATE) - 3 AND COUNT(DISTINCT ga.game_id) >= 5
        )
        SELECT 
            ge.game_engine_name AS engine,
            COUNT(DISTINCT cd.game_id) AS game_count,
            COUNT(DISTINCT cd.company_id) AS developer_count
        FROM active_developers ad
        JOIN companies_developed cd ON ad.company_id = cd.company_id
        JOIN games ga ON cd.game_id = ga.game_id
        JOIN games_game_engines gge ON ga.game_id = gge.game_id
        JOIN game_engines ge ON gge.game_engine_id = ge.game_engine_id
        WHERE ga.total_rating_count >= 30
        GROUP BY ge.game_engine_name
        ORDER BY game_count DESC
        LIMIT {top_n};
    """)

    return [{'engine': result[0], 'game_count': result[1], 'developer_count': result[2]} for result in cur.fetchall()]

# Heatmap
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
            WHERE ga.total_rating_count >= 30 AND release_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 15
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
        ) gr
        WHERE gr.genre_rank <= 10
        ORDER BY release_year ASC, genre_rank ASC
    """)

    return [{'genre': result[0], 'release_year': result[1], 'weighted_average_rating': result[2]} for result in cur.fetchall()]