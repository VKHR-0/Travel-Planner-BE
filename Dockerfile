FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry && poetry install --no-root

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
