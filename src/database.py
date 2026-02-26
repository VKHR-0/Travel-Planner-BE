import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://travel_user:travel_pass@db:5432/travel_planner",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL)
