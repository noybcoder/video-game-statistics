import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5