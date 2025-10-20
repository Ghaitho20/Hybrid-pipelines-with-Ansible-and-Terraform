import os
import pytest
from unittest.mock import patch, MagicMock



# Mock psycopg2 and sqlalchemy before importing app
with patch('psycopg2.connect'), \
     patch('sqlalchemy.create_engine') as mock_engine:
    
    # Now import your app
    from app import app

# Create a fixture for the mock engine
@pytest.fixture
def mock_db_engine():
    with patch('app.engine') as mock_engine:
        yield mock_engine

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Your tests remain the same...
# ----------------------
# Mock for /api/trees/stats/arrondissements
# ----------------------
@patch('app.engine.connect')
def test_trees_by_arrondissement(mock_connect, client):
    class MockResult:
        def __iter__(self):
            return iter([("PARIS 1ER", 50), ("PARIS 2E", 30)])
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_conn.execute.return_value = MockResult()

    response = client.get('/api/trees/stats/arrondissements')
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]['arrondissement'] == "PARIS 1ER"
    assert data[0]['count'] == 50

# ----------------------
# Mock for /api/trees/stats/species
# ----------------------
@patch('app.engine.connect')
def test_trees_by_species(mock_connect, client):
    class MockResult:
        def __iter__(self):
            return iter([("Chêne", 10), ("Platane", 5)])
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_conn.execute.return_value = MockResult()

    response = client.get('/api/trees/stats/species')
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]['espece'] == "Chêne"
    assert data[0]['count'] == 10

# ----------------------
# Mock for /api/trees/stats/height
# ----------------------
@patch('app.engine.connect')
def test_trees_height_stats(mock_connect, client):
    class MockResult:
        def __iter__(self):
            return iter([
                ("Chêne", 10.5, 20.0, 6),
                ("Platane", 8.0, 15.0, 10)
            ])
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_conn.execute.return_value = MockResult()

    response = client.get('/api/trees/stats/height')
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]['espece'] == "Chêne"
    assert data[0]['avg_height'] == 10.5
    assert data[0]['max_height'] == 20.0
    assert data[0]['count'] == 6

# ----------------------
# Mock for /api/trees/stats/remarkable
# ----------------------
@patch('app.engine.connect')
def test_remarkable_trees(mock_connect, client):
    class MockResult:
        def __iter__(self):
            return iter([
                ("PARIS 1ER", 50, 10),
                ("PARIS 2E", 30, 5)
            ])
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_conn.execute.return_value = MockResult()

    response = client.get('/api/trees/stats/remarkable')
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]['arrondissement'] == "PARIS 1ER"
    assert data[0]['total_trees'] == 50
    assert data[0]['remarkable_trees'] == 10
    assert data[0]['remarkable_percentage'] == 20.0

# ----------------------
# Mock for /api/trees/geolocation
# ----------------------
@patch('app.engine.connect')
def test_trees_geolocation(mock_connect, client):
    class MockResult:
        def __iter__(self):
            return iter([
                (1, "Tree1", "Chêne", 10.0, 0.5, 1, 2.3522, 48.8566),
                (2, "Tree2", "Platane", 8.0, 0.3, 0, 2.3600, 48.8570)
            ])
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_conn.execute.return_value = MockResult()

    response = client.get('/api/trees/geolocation')
    data = response.get_json()

    assert response.status_code == 200
    assert data[0]['id'] == 1
    assert data[0]['nom'] == "Tree1"
    assert data[0]['espece'] == "Chêne"
    assert data[0]['longitude'] == 2.3522
    assert data[0]['latitude'] == 48.8566

# ----------------------
# Test for /metrics endpoint
# ----------------------
def test_metrics(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'http_requests_total' in response.data
