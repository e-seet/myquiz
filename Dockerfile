FROM python:3.11-slim

WORKDIR /app

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

COPY app/ ./app/

# Set up Git inside the container
RUN apt-get update && apt-get install -y git

# Ports + CMD overridden in docker-compose
EXPOSE 5001