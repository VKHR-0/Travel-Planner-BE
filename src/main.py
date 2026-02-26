from fastapi import FastAPI

from src.routers.projects import router as projects_router

app = FastAPI(
    title="Travel Planner API",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(projects_router)


@app.get("/")
def read_root():
    return {"service": "travel-planner", "status": "ok"}
