FROM python:3.9

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Start service
COPY main.py .
CMD ["python", "main.py"]

