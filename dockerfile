FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUNICORN_WORKERS=3 \
    GUNICORN_TIMEOUT=60

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /data
ENV DB_PATH=/data/habits.db

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]
