from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.clients.artic import ArticClient
from src.database import get_db
from src.deps import get_artic_client
from src.schemas import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectWithPlacesResponse,
)
from src.services.projects import (
    create_project,
    get_project,
    list_projects,
    update_project,
)


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "", response_model=ProjectWithPlacesResponse, status_code=status.HTTP_201_CREATED
)
async def create_project_endpoint(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    artic_client: ArticClient = Depends(get_artic_client),
) -> ProjectWithPlacesResponse:
    return await create_project(db, payload, artic_client)


@router.get("", response_model=list[ProjectResponse])
def list_projects_endpoint(db: Session = Depends(get_db)) -> list[ProjectResponse]:
    return list_projects(db)


@router.get("/{project_id}", response_model=ProjectWithPlacesResponse)
def get_project_endpoint(
    project_id: int, db: Session = Depends(get_db)
) -> ProjectWithPlacesResponse:
    return get_project(db, project_id)


@router.patch("/{project_id}", response_model=ProjectWithPlacesResponse)
def update_project_endpoint(
    project_id: int,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectWithPlacesResponse:
    return update_project(db, project_id, payload)
