# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080 to match Azure Web App configuration
EXPOSE 8181

# Update the Flask port to 8080
ENV PORT=8181

# Run the Flask app
CMD ["python", "main.py"]