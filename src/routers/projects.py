from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.clients.artic import ArticClient
from src.database import get_db
from src.deps import get_artic_client
from src.schemas import (
    ProjectCreateRequest,
    ProjectPlaceCreateRequest,
    ProjectPlaceResponse,
    ProjectPlaceUpdateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectWithPlacesResponse,
)
from src.services.projects import (
    add_project_place,
    create_project,
    get_project,
    get_project_place,
    list_project_places,
    list_projects,
    update_project_place,
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


@router.post(
    "/{project_id}/places",
    response_model=ProjectPlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_place_endpoint(
    project_id: int,
    payload: ProjectPlaceCreateRequest,
    db: Session = Depends(get_db),
    artic_client: ArticClient = Depends(get_artic_client),
) -> ProjectPlaceResponse:
    return await add_project_place(db, project_id, payload, artic_client)


@router.get("/{project_id}/places", response_model=list[ProjectPlaceResponse])
def list_project_places_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[ProjectPlaceResponse]:
    return list_project_places(db, project_id)


@router.get("/{project_id}/places/{place_id}", response_model=ProjectPlaceResponse)
def get_project_place_endpoint(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
) -> ProjectPlaceResponse:
    return get_project_place(db, project_id, place_id)


@router.patch("/{project_id}/places/{place_id}", response_model=ProjectPlaceResponse)
def update_project_place_endpoint(
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectPlaceResponse:
    return update_project_place(db, project_id, place_id, payload)
