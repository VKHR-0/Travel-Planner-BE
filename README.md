## Run with Docker Compose

1. Copy env file:

```bash
cp .env.example .env
```

2. Start PostgreSQL and API:

```bash
docker compose up --build
```

3. Run Alembic migrations:

```bash
docker compose --profile tools run --rm migrate
```

The API is available at `http://localhost:8000`.
