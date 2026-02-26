from fastapi import FastAPI

app = FastAPI(title="Travel Planner API", version="0.1.0")


@app.get("/")
def read_root():
    return {"service": "travel-planner", "status": "ok"}
