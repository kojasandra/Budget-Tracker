from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from model.base import Base


@pytest.fixture
def test_session():
    # Create in memory database for tests
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def configure(connection, record):
        connection.create_function("char_length", 1, len)
        connection.execute("PRAGMA foreign_keys=ON")

    # Creating tables for tests
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    with patch("services.summary.Session", TestSession):
        with patch("services.transaction_import.Session", TestSession):
            with patch("services.categories.Session", TestSession):
                with patch("services.budgets.Session", TestSession):
                    with patch("services.transactions.Session", TestSession):
                        with TestSession() as db:
                            yield db

    engine.dispose()

@pytest.fixture
def client(test_session):
    with TestClient(app) as client:
        yield client
