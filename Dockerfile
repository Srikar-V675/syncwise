
# Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    unzip \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Get the version of Chromium installed and download the corresponding ChromeDriver
RUN CHROMIUM_VERSION=$(chromium --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    echo "Chromium version: $CHROMIUM_VERSION" && \
    wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROMIUM_VERSION/linux64/chromedriver-linux64.zip && \
    echo "Downloading ChromeDriver for version $CHROMIUM_VERSION" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver-linux64/chromedriver && \
    ln -s /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# RUN python manage.py makemigrations
# RUN python manage.py migrate
# RUN python manage.py create_groups
