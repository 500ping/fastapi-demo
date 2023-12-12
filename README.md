# DESCRIPTION

Demo project for fastapi.

## Installation

```bash
pip install -r requirements.txt
```

## Init DB

```bash
alembic upgrade head
```

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Docker

```bash
docker build -t fast-demo:latest .
docker run -p 8000:8080 fast-demo
```
