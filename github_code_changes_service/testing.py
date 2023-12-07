import requests
from flask import Flask, jsonify, request
import mysql.connector
import boto3

app = Flask(__name__)

# Function to retrieve the database password from AWS Secrets Manager
def get_secret():
    secret_name = "rds_db"  # Replace with your actual secret name
    region_name = "us-east-1"  # Replace with your AWS region

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
        return None

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return secret
    else:
        print("Secrets Manager response does not contain 'SecretString'.")
        return None

# Establish a connection to the database
def create_connection():
    secret = get_secret()

    if secret is not None:
        secret_dict = eval(secret)
        connection = mysql.connector.connect(
            host=secret_dict.get("host"),
            user=secret_dict.get("user"),
            password=secret_dict.get("password"),
            database=secret_dict.get("database")
        )
        return connection
    else:
        return None

# Call create_connection() function to establish a connection to the database
db = create_connection()

# Endpoint for getting GitHub code changes
# Example URL: http://127.0.0.1:5000/get_github_code_changes?owner_username=SachiniTen&repository=Bootcamp&developer_username=SachiniTen
@app.route('/get_github_code_changes', methods=['GET'])
def get_github_code_changes():
    # Get parameters from the request URL
    owner_username = request.args.get('owner_username')
    repository = request.args.get('repository')
    developer_username = request.args.get('developer_username')

    # Check if required parameters are missing
    if owner_username is None or repository is None or developer_username is None:
        return jsonify({'error': 'Missing required parameters'}), 400

    # GitHub API URL to retrieve contributor statistics
    contributor_stats_url = f"https://api.github.com/repos/{owner_username}/{repository}/stats/contributors"
    response = requests.get(contributor_stats_url)

    # GitHub API URL to retrieve repository details
    repo_details_url = f"https://api.github.com/repos/{owner_username}/{repository}"
    repo_details_response = requests.get(repo_details_url)

    # Check for successful API responses
    if response.status_code == 200 and repo_details_response.status_code == 200:
        contributors_data = response.json()
        repo_details_data = repo_details_response.json()

        # Filter contributions for the target user
        target_contributor = next(
            (contributor for contributor in contributors_data if contributor['author']['login'] == developer_username),
            None)

        if target_contributor:
            # Calculate added and deleted lines
            added_lines = sum(week['a'] for week in target_contributor['weeks'])
            deleted_lines = sum(week['d'] for week in target_contributor['weeks'])

            # Total file count in the repository
            total_files_count = repo_details_data.get('size', 0)

            # Insert data into the database
            cursor = db.cursor()
            insert_query = (
                "INSERT INTO DeveloperIQ_db.github_code_changes(developer_username, repository, owner, "
                "added_lines_count, deleted_lines_count, total_files_count) VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(insert_query, (
            developer_username, repository, owner_username, added_lines, deleted_lines, total_files_count))
            db.commit()

            # Return JSON response with code changes
            return jsonify({
                'added_lines': added_lines,
                'deleted_lines': deleted_lines,
                'total_files_count': total_files_count,
            })
        else:
            print(f"Contributions not found for user '{developer_username}'.")
            return jsonify({'error': f"Contributions not found for user '{developer_username}'"})
    else:
        print(f"Error: {response.status_code}")
        return jsonify({'error': f"Error: {response.status_code}"})


# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
