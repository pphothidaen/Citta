FROM python:3.11-slim

WORKDIR /app

COPY docker/node4/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/node4/edge_worker.py edge_worker.py
COPY docker/node4/queue_consumer.py queue_consumer.py

CMD ["python", "edge_worker.py"]