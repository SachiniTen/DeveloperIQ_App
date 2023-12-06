import requests
from urllib.parse import parse_qs, urlparse
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Establish a connection to the database
def create_connection():
    connection = mysql.connector.connect(
        host="mydbinstance.c5n54ozmyizd.us-east-1.rds.amazonaws.com",
        user="admin",
        password="sachten123",
        database="DeveloperIQ_db"
    )
    return connection

# Call create_connection() function to establish a database connection
db = create_connection()

def get_repo_commits(owner_name, repo_name, developer_user):
    """
    Returns the number of commits to a GitHub repository.
    """
    # Construct the API URL for the last page of commits
    url = f"https://api.github.com/repos/{owner_name}/{repo_name}/commits?per_page=1"
    r = requests.get(url)

    # Check if the request was successful
    if r.status_code == 200:
        # Extract the information from the "Link" header to get the total number of pages
        links = r.links
        rel_last_link_url = urlparse(links["last"]["url"])
        rel_last_link_url_args = parse_qs(rel_last_link_url.query)
        rel_last_link_url_page_arg = rel_last_link_url_args["page"][0]
        commits_count = int(rel_last_link_url_page_arg)

        # If a developer_user is provided, retrieve and return the commits made by that user
        if developer_user:
            user_commits = get_user_commits(owner_name, repo_name, developer_user)
            return commits_count, user_commits

        return commits_count
    else:
        print(f"Error: {r.status_code}")
        return None

def get_user_commits(owner_name, repo_name, developer_user):
    """
    Returns the commits made by a specific user in a GitHub repository.
    """
    # Construct the API URL for the commits made by the developer_user
    url = f"https://api.github.com/repos/{owner_name}/{repo_name}/commits"
    params = {'author': developer_user}
    r = requests.get(url, params=params)

    # Check if the request was successful
    if r.status_code == 200:
        user_commits = r.json()
        return user_commits
    else:
        print(f"Error: {r.status_code}")
        return None

# Example usage
# http://127.0.0.1:5000/get_github_commits_count_main?owner_username=SachiniTen&repository_name=Bootcamp&developer_username=SachiniTen
@app.route('/get_github_commits_count_main', methods=['GET'])
def get_github_commits_count_main():
    # Retrieve parameters from the request URL
    owner_username = request.args.get('owner_username')
    repository_name = request.args.get('repository_name')
    developer_username = request.args.get('developer_username')

    # Check for missing parameters
    if owner_username is None or repository_name is None or developer_username is None:
        return jsonify({'error': 'Missing required parameters'}), 400

    # Call the function to get repository commits and user commits if developer_username is provided
    repo_commits_count, user_commits = get_repo_commits(owner_username, repository_name, developer_username)

    # Check if data retrieval was successful
    if repo_commits_count is not None:
        print(f"Total Commits: {repo_commits_count}")

        # If developer_username is provided, print user commits details
        if developer_username and user_commits is not None:
            print(f"Commits by {developer_username}:")
            user_commits_count = 0
            for commit in user_commits:
                user_commits_count += 1
                print(commit['sha'], commit['commit']['message'])
            print(user_commits_count)
    else:
        print("Error retrieving data.")

    # Insert data into the database
    cursor = db.cursor()
    insert_query = "INSERT INTO DeveloperIQ_db.github_user_commits(developer_username, repository, owner, repo_commits_count, developer_commits_count) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (developer_username, repository_name, owner_username, repo_commits_count, user_commits_count))
    db.commit()
    print("Recorded inserted")
    return jsonify({
        'Repository commits count': repo_commits_count,
        'User commits count': user_commits_count
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
