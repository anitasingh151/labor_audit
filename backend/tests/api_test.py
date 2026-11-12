# Language: python
import pytest
from backend.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_costs(client):
    response = client.get('/api/costs')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == [{"cost_type": 1, "status": "A"}]