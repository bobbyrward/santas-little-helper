"""Database connection and session management."""

from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from santas_little_helper.models import Base


def get_db_path() -> Path:
    """Get the database file path."""
    home = Path.home()
    db_dir = home / ".santas-little-helper"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "orders.db"


def get_engine():
    """Create and return database engine."""
    db_path = get_db_path()
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db():
    """Initialize the database schema."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session_factory():
    """Create and return session factory."""
    engine = get_engine()
    return sessionmaker(bind=engine)


@contextmanager
def get_session():
    """Get database session."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
