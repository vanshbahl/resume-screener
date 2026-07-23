import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.database import Base, get_db
from app.main import app


# Use testcontainers to spin up a PostgreSQL instance for the test session
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("pgvector/pgvector:pg16", dbname="test_db") as postgres:
        yield postgres


# Create the SQLAlchemy engine tied to the Testcontainer
@pytest.fixture(scope="session")
def db_engine(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    # Create all tables (in a real scenario with complex migrations, we'd run alembic upgrade head here)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


# Session scope factory
@pytest.fixture(scope="session")
def SessionLocal(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


# Function-scoped fixture to provide isolated transactions per test
@pytest.fixture(scope="function")
def db_session(db_engine, SessionLocal) -> Session:
    connection = db_engine.connect()
    # Begin a non-ORM transaction
    transaction = connection.begin()

    # Bind an individual Session to the connection
    session = SessionLocal(bind=connection)

    yield session

    # Teardown: Rollback the transaction to clear test data, close session and connection
    session.close()
    transaction.rollback()
    connection.close()


# Provide a FastAPI TestClient with the isolated db_session
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
