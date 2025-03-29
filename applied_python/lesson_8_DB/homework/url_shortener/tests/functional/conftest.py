import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_FILE = tempfile.mktemp(suffix='.db')
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"

from db import Base, get_db
from main import app


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        f"sqlite:///{TEST_DB_FILE}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

    try:
        os.unlink(TEST_DB_FILE)
    except:
        pass


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, db_session):
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    client.post("/register", json={
        "username": "testuser",
        "password": "testpass"
    })

    response = client.post("/login",
                           data={"username": "testuser", "password": "testpass"},
                           headers={"Content-Type": "application/x-www-form-urlencoded"}
                           )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
