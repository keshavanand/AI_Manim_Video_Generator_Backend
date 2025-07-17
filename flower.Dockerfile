# Dockerfile.flower

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Flower
RUN pip install --no-cache-dir flower==2.0.1

# Expose Flower default port
EXPOSE 5555

# Command to start Flower with Redis as the broker (can be overridden)
CMD ["python", "-m", "flower", "flower", "--port=5555", "--broker=redis://redis:6379/0"]
