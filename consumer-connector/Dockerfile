# Consumer Connector Dockerfile
# Optimized for Google Cloud Run

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module
COPY ../shared /app/shared

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8081
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8081

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
