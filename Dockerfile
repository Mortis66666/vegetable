# Use official Python runtime as base image
# Explicitly specify linux/amd64 platform
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]