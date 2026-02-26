# Travel Planner Backend

FastAPI backend for managing travel projects and places (validated against the Art Institute of Chicago API).

## Requirements

- Docker + Docker Compose
- (Optional for local non-Docker run) Python 3.13 and Poetry

## Build and start (recommended: Docker)

1. Create env file.

```bash
cp .env.example .env
```

2. Build and start services.

```bash
docker compose up --build -d
```

3. Run database migrations.

```bash
docker compose --profile tools run --rm migrate
```

4. Open API docs.

- Swagger UI: `http://localhost:8000/swagger`
- ReDoc: `http://localhost:8000/redoc`

## Environment variables

The app reads variables from `.env` (used by Docker Compose).

- `POSTGRES_DB` default: `travel_planner`
- `POSTGRES_USER` default: `travel_user`
- `POSTGRES_PASSWORD` default: `travel_pass`
- `DATABASE_URL` default: `postgresql+psycopg://travel_user:travel_pass@db:5432/travel_planner`

## Run locally without Docker (optional)

1. Install dependencies.

```bash
poetry install
```

2. Run migrations.

```bash
poetry run alembic upgrade head
```

3. Start API.

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
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

## Example requests

Create a project with imported places:

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Barcelona Art Week",
    "description": "Modern art route",
    "start_date": "2026-06-01",
    "places": [
      {"external_id": 129884, "notes": "Prioritize this one"},
      {"external_id": 27992}
    ]
  }'
```

Add a place to an existing project:

```bash
curl -X POST http://localhost:8000/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"external_id": 111628, "notes": "Check opening hours"}'
```

Update notes and mark place visited:

```bash
curl -X PATCH http://localhost:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"notes": "Visited in the morning", "visited": true}'
```

Delete a project:

```bash
curl -X DELETE http://localhost:8000/projects/1
```

## Business rules

- Project creation requires at least 1 place and allows at most 10 places.
- The same external place cannot be added to the same project twice.
- Places are validated against the Art Institute API before storing.
- Project completion is computed dynamically when all project places are visited.
- A project cannot be deleted if any of its places is visited.

## Useful commands

Check compose file:

```bash
docker compose config
```

Compile-time sanity check:

```bash
poetry run python -m compileall src alembic
```

Stop services:

```bash
docker compose down
```
