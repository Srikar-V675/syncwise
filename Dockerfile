# Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

