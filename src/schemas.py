from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PlaceImportRequest(BaseModel):
    external_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=5000)


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None
    places: list[PlaceImportRequest] = Field(min_length=1, max_length=10)


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None


class ProjectPlaceCreateRequest(BaseModel):
    external_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=5000)


class ProjectPlaceUpdateRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)
    visited: bool | None = None


class ProjectPlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: str
    artist_title: str | None
    image_id: str | None
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    start_date: date | None
    completed: bool
    places_count: int
    created_at: datetime
    updated_at: datetime


class ProjectWithPlacesResponse(ProjectResponse):
    places: list[ProjectPlaceResponse]
