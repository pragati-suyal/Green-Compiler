FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r backend/requirements.txt

RUN g++ -std=c++17 -O2 analyzer/main.cpp -o analyzer/green_compiler

EXPOSE 10000

CMD ["sh", "-c", "cd backend && gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
