from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.clients.artic import (
    ArticArtwork,
    ArticArtworkNotFoundError,
    ArticClient,
    ArticClientError,
)
from src.models import Project, ProjectPlace
from src.schemas import (
    PlaceImportRequest,
    ProjectCreateRequest,
    ProjectPlaceCreateRequest,
    ProjectPlaceResponse,
    ProjectPlaceUpdateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectWithPlacesResponse,
)


def _compute_completed(places: list[ProjectPlace]) -> bool:
    return len(places) > 0 and all(place.visited for place in places)


def _to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        completed=_compute_completed(project.places),
        places_count=len(project.places),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _to_project_with_places_response(project: Project) -> ProjectWithPlacesResponse:
    base = _to_project_response(project)
    return ProjectWithPlacesResponse(**base.model_dump(), places=project.places)


def _to_project_place_response(project_place: ProjectPlace) -> ProjectPlaceResponse:
    return ProjectPlaceResponse.model_validate(project_place)


def _get_project_or_404(db: Session, project_id: int) -> Project:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    project = db.execute(stmt).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_project_place_or_404(
    db: Session, project_id: int, place_id: int
) -> ProjectPlace:
    stmt = select(ProjectPlace).where(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id,
    )
    project_place = db.execute(stmt).scalar_one_or_none()
    if project_place is None:
        raise HTTPException(status_code=404, detail="Project place not found")
    return project_place


def _validate_imported_places(places: list[PlaceImportRequest]) -> None:
    if len(places) > 10:
        raise HTTPException(
            status_code=409, detail="A project can contain at most 10 places"
        )

    external_ids = [place.external_id for place in places]
    if len(external_ids) != len(set(external_ids)):
        raise HTTPException(
            status_code=409, detail="Duplicate external place IDs are not allowed"
        )


async def _fetch_artworks(
    artic_client: ArticClient, places: list[PlaceImportRequest]
) -> list[ArticArtwork]:
    artworks: list[ArticArtwork] = []
    for place in places:
        try:
            artwork = await artic_client.get_artwork(place.external_id)
        except ArticArtworkNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ArticClientError as exc:
            raise HTTPException(
                status_code=502, detail="Failed to validate place in Art Institute API"
            ) from exc
        artworks.append(artwork)

    return artworks


async def create_project(
    db: Session, payload: ProjectCreateRequest, artic_client: ArticClient
) -> ProjectWithPlacesResponse:
    _validate_imported_places(payload.places)
    artworks = await _fetch_artworks(artic_client, payload.places)

    project = Project(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    db.add(project)
    db.flush()

    places_by_external_id = {place.external_id: place for place in payload.places}
    for artwork in artworks:
        place_payload = places_by_external_id[artwork.external_id]
        project_place = ProjectPlace(
            project_id=project.id,
            external_id=artwork.external_id,
            title=artwork.title,
            artist_title=artwork.artist_title,
            image_id=artwork.image_id,
            notes=place_payload.notes,
            visited=False,
        )
        db.add(project_place)

    db.commit()

    return get_project(db, project.id)


def list_projects(db: Session) -> list[ProjectResponse]:
    stmt = select(Project).options(selectinload(Project.places)).order_by(Project.id)
    projects = db.execute(stmt).scalars().all()
    return [_to_project_response(project) for project in projects]


def get_project(db: Session, project_id: int) -> ProjectWithPlacesResponse:
    project = _get_project_or_404(db, project_id)
    return _to_project_with_places_response(project)


def update_project(
    db: Session, project_id: int, payload: ProjectUpdateRequest
) -> ProjectWithPlacesResponse:
    project = _get_project_or_404(db, project_id)

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    _ = project.places
    return _to_project_with_places_response(project)


async def add_project_place(
    db: Session,
    project_id: int,
    payload: ProjectPlaceCreateRequest,
    artic_client: ArticClient,
) -> ProjectPlaceResponse:
    project = _get_project_or_404(db, project_id)

    if len(project.places) >= 10:
        raise HTTPException(
            status_code=409, detail="A project can contain at most 10 places"
        )

    existing = db.execute(
        select(ProjectPlace).where(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == payload.external_id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="Place already exists in this project"
        )

    try:
        artwork = await artic_client.get_artwork(payload.external_id)
    except ArticArtworkNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArticClientError as exc:
        raise HTTPException(
            status_code=502, detail="Failed to validate place in Art Institute API"
        ) from exc

    project_place = ProjectPlace(
        project_id=project_id,
        external_id=artwork.external_id,
        title=artwork.title,
        artist_title=artwork.artist_title,
        image_id=artwork.image_id,
        notes=payload.notes,
        visited=False,
    )
    db.add(project_place)
    db.commit()
    db.refresh(project_place)
    return _to_project_place_response(project_place)


def list_project_places(db: Session, project_id: int) -> list[ProjectPlaceResponse]:
    _get_project_or_404(db, project_id)
    stmt = (
        select(ProjectPlace)
        .where(ProjectPlace.project_id == project_id)
        .order_by(ProjectPlace.id)
    )
    project_places = db.execute(stmt).scalars().all()
    return [
        _to_project_place_response(project_place) for project_place in project_places
    ]


def get_project_place(
    db: Session, project_id: int, place_id: int
) -> ProjectPlaceResponse:
    project_place = _get_project_place_or_404(db, project_id, place_id)
    return _to_project_place_response(project_place)


def update_project_place(
    db: Session,
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdateRequest,
) -> ProjectPlaceResponse:
    project_place = _get_project_place_or_404(db, project_id, place_id)

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(project_place, key, value)

    db.commit()
    db.refresh(project_place)
    return _to_project_place_response(project_place)


def delete_project(db: Session, project_id: int) -> None:
    project = _get_project_or_404(db, project_id)

    if any(place.visited for place in project.places):
        raise HTTPException(
            status_code=409,
            detail="Project cannot be deleted because it has visited places",
        )

    db.delete(project)
    db.commit()
