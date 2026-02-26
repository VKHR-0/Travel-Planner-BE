# Travel Planner API

FastAPI backend for managing travel projects and places validated against the Art Institute of Chicago API.

## Setup

1. Copy environment file.

```bash
cp .env.example .env
```

2. Start PostgreSQL and API.

```bash
docker compose up --build
```

3. Apply migrations.

```bash
docker compose --profile tools run --rm migrate
```

API base URL: `http://localhost:8000`

## Migrations

- Upgrade to latest revision:

```bash
poetry run alembic upgrade head
```

- Downgrade to base:

```bash
poetry run alembic downgrade base
```

## API endpoints

Projects:

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`

Project places:

- `POST /projects/{project_id}/places`
- `GET /projects/{project_id}/places`
- `GET /projects/{project_id}/places/{place_id}`
- `PATCH /projects/{project_id}/places/{place_id}`

## Key business rules

- Project creation requires at least 1 place and allows at most 10 places.
- The same external place cannot be added to the same project twice.
- Places are validated against the Art Institute API before being stored.
- Project completion is computed dynamically when all project places are visited.
- A project cannot be deleted if any of its places is marked as visited.

## Quick verify

```bash
poetry run python -m compileall src alembic
docker compose config
```
