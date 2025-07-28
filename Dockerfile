FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY extract_headings.py .
CMD ["python", "extract_headings.py"]
