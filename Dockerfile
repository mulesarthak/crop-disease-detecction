# Backend Dockerfile for Crop Disease Detection
FROM python:3.9-slim

WORKDIR /app

# Copy backend files
COPY server/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()"

# Run the application with Uvicorn
CMD ["python", "main.py"]
