# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy backend files
COPY server/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (adjust based on your backend port)
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
