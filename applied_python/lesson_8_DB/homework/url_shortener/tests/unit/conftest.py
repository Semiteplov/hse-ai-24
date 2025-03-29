import pytest
from db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    client.post("/register", json={
        "username": "testuser",
        "password": "testpass"
    })

    response = client.post("/login",
                           data={"username": "testuser", "password": "testpass"},
                           headers={"Content-Type": "application/x-www-form-urlencoded"}
                           )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

