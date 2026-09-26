import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    with TestClient(app) as client:
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5

def test_platforms_by_year():
    with TestClient(app) as client:
        response = client.get('/analytics/most_popular_platforms_by_year')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) == {'platform', 'release_year', 'game_count'}

def test_genre_by_market_share():
    with TestClient(app) as client:
        response = client.get('/analytics/genre_distribution')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) == {'genre', 'game_count'}

def test_game_genres_by_developer():
    with TestClient(app) as client:
        response = client.get('/analytics/genres_per_developer')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) == {'developer', 'genre', 'total_game_count', 'pct_of_total_game_count'}

def test_game_engine_by_developer():
    with TestClient(app) as client:
        response = client.get('/analytics/top_n_game_engines')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) == {'engine', 'game_count', 'developer_count'}

def test_genres_by_year():
    with TestClient(app) as client:
        response = client.get('/analytics/most_popular_genres_by_year')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) == {'genre', 'release_year', 'weighted_average_rating'}