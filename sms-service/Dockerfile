# Use official Python 3.12 image
FROM python:3.12-slim

# Set environment variables

ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependencies first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment file
COPY .env .env

# Copy application code
COPY app ./app

# RQ worker does NOT need any exposed ports
# Run RQ worker directly
CMD ["rq", "worker", "queue:sms:otp"]
