import pytest
from unittest.mock import MagicMock, patch
from github_code_changes_service import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_github_code_changes_success(client):
    with patch('github_code_changes_service.requests.get') as mock_get:
        # Mock successful API responses
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: [{'author': {'login': 'test_user'}, 'weeks': [{'a': 1, 'd': 1}]}]),
            MagicMock(status_code=200, json=lambda: {'size': 10}),
        ]

        response = client.get('/get_github_code_changes?owner_username=test&repository=test&developer_username=test_user')

        assert response.status_code == 200
        data = response.json
        assert 'added_liness' in data
        assert 'deleted_lines' in data
        assert 'total_files_count' in data

def test_get_github_code_changes_missing_parameters(client):
    response = client.get('/get_github_code_changes')

    assert response.status_code == 400
    assert b'Missing required parameters' in response.data

def test_get_github_code_changes_contributions_not_found(client):
    with patch('github_code_changes_service.requests.get') as mock_get:
        # Mock API response with missing contributions
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: []),
            MagicMock(status_code=200, json=lambda: {'size': 10}),
        ]

        response = client.get('/get_github_code_changes?owner_username=test&repository=test&developer_username=test_user')

        assert response.status_code == 200
        data = response.json
        assert 'error' in data
        assert b"Contributions not found for user 'test_user'" in response.data

def test_get_github_code_changes_api_error(client):
    with patch('github_code_changes_service.requests.get') as mock_get:
        # Mock API response with an error
        mock_get.side_effect = [MagicMock(status_code=500), MagicMock(status_code=200, json=lambda: {'size': 10})]

        response = client.get('/get_github_code_changes?owner_username=test&repository=test&developer_username=test_user')

        assert response.status_code == 200
        data = response.json
        assert 'error' in data
        assert b"Error: 500" in response.data
