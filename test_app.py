import pytest
from app.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Test the index page."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Get Your Personalized Plan' in rv.data  # Update this line to match the actual text in your index.html

def test_recommend(client):
    """Test the recommendation functionality."""
    rv = client.post('/recommend', data={
        'sex': '1',
        'age': '25',
        'height': '1.75',
        'weight': '70',
        'hypertension': '0',
        'diabetes': '0',
        'bmi': '22.9',
        'level': '0',
        'fitness_goal': '1',
        'fitness_type': '0'
    })
    assert rv.status_code == 200
    assert b'Your Personalized Workout Plan' in rv.data  # Update this line to match the actual text in your recommendations.html