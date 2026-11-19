# Dockerfile mẫu cho backend (FastAPI / Python)
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "if [ -f main.py ]; then uvicorn main:app --host 0.0.0.0 --port 8000; else echo 'Backend source code not mounted/found' && tail -f /dev/null; fi"]
