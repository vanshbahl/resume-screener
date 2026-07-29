import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URI
try:
    engine = create_engine(
        db_url,
        connect_args={"connect_timeout": 2} if "postgresql" in db_url else {},
    )
    with engine.connect() as conn:
        pass
except Exception as exc:
    logger.warning(
        "PostgreSQL unreachable (%s). Falling back to local SQLite (sqlite:///./app.db).",
        exc,
    )
    db_url = "sqlite:///./app.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
