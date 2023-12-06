# Dockerfile_user_commits_service
FROM python:3.10-slim

WORKDIR /app

COPY github_user_commits_service/requirements.txt .
RUN pip install --no-cache-dir -r github_user_commits_service/requirements.txt

COPY . .

CMD ["python", "github_user_commits_service.py"]
