FROM python:3.9

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add application code
COPY healthcheck.py .
COPY test_apigateway.py .
