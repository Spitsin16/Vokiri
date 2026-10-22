import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

import backend.models.dictionary
import backend.models.text
import backend.models.user
import backend.models.user_word

@pytest.fixture
def db_session(tmp_path):
    database_path = tmp_path / "test.db"
    database_url = f"sqlite:///{database_path}"

    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(test_engine)

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    with TestSessionLocal() as session:
        yield session

    Base.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

@pytest.fixture
def authenticated_user(client):
    email = "test@mail.com"
    password = "qwerty1234"
    register_response = client.post("/auth/register", json = {"email": email,
                                          "password": password})
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json = {"email": email,
                                          "password": password})
    assert login_response.status_code == 200

    body = login_response.json()
    token = body["access_token"]

    return {"email": email,
            "password": password,
            "token": token,
            "headers": {"Authorization":f"Bearer {token}"}}
