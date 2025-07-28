FROM ghcr.io/nlmatics/nlm-ingestor:latest

WORKDIR /app

RUN pip install --no-cache-dir llmsherpa==0.1.4

COPY extract_headings.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
