import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.user import User


@pytest.fixture
def db_session(tmp_path):
    database_path = tmp_path / "test.db"
    database_url = f"sqlite:///{database_path}"

    test_engine = create_engine(database_url)

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