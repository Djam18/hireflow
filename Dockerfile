FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary==2.9.3

COPY . .

WORKDIR /app/hireflow

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
