# Dockerfile_code_changes_service
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "github_code_changes_service/github_code_changes_service.py"]
