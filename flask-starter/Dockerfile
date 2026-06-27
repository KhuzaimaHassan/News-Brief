# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for oracledb (Thick mode requires Oracle Instant Client, but we use Thin mode which only needs Python)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run setup script to decode Base64 secrets, then start gunicorn
CMD python render_setup.py && gunicorn --bind 0.0.0.0:5000 app:app
