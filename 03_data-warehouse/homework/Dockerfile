FROM python:3.9-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy script and credentials
COPY load_yellow_taxi_data.py .
COPY gcs.json .

# Install dependencies using uv
RUN uv pip install --system google-cloud-storage

# Run the script
CMD ["python", "load_yellow_taxi_data.py"]