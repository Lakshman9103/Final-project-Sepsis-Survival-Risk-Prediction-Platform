# Use official Python runtime
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit app
CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

