import pytest
from unittest.mock import patch
from github_user_activity_service import app  # Replace 'your_module' with the actual filename

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_github_commits_count_main(client):
    with patch('github_user_activity_service.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.links = {'last': {'url': 'https://example.com?per_page=30&page=2'}}
        mock_get.return_value.json.return_value = [{'sha': '123', 'commit': {'message': 'Test commit'}}]

        response = client.get('/get_github_commits_count_main?owner_username=test&repository_name=test&developer_username=test')

        assert response.status_code == 200

        assert b'Repository commits count' in response.data
        assert b'User commits count' in response.data


def test_get_github_pull_requests(client):
    with patch('github_user_activity_service.requests.get') as mock_get:  # Replace 'your_module' with the actual filename
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{'number': 1}, {'number': 2}]

        response = client.get('/get_github_pull_requests?owner_username=test&repository=test&developer_username=test')

        assert response.status_code == 200
        assert b'Assigned Pull Requests' in response.data
        assert b'Total Pull Requests' in response.data

def test_get_github_issues(client):
    with patch('github_user_activity_service.requests.get') as mock_get:  # Replace 'your_module' with the actual filename
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{'state': 'open'}, {'state': 'closed'}]

        response = client.get('/get_github_issues?owner_username=test&repository=test&developer_username=test')

        assert response.status_code == 200
        assert b'Assigned Issues' in response.data
        assert b'Total Issues' in response.data
        assert b'Repo Open Issues Count' in response.data
        assert b'Repo Closed Issues Count' in response.data
        assert b'Developer Open Issues Count' in response.data
        assert b'Developer Closed Issues Count' in response.data
