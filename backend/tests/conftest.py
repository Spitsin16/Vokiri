import pytest
from uuid import uuid4

import backend.models.activity
import backend.models.dictionary
import backend.models.text
import backend.models.user
import backend.models.user_word

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

from backend.models.dictionary import (
    Definition,
    DictionarySource,
    Lexeme,
    Pronunciation,
    SourceSense,
    Translation,
)
from backend.models.text import AllText
from backend.models.user import User

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

@pytest.fixture
def create_text(db_session):
    text = AllText(
        title="Football story",
        theme="Football",
        level="B1",
        target_words=[
            {
                "word": "achieve",
                "translation": "достигать",
            }
        ],
        word_count=100,
        content="Test English text.",
    )

    db_session.add(text)
    db_session.flush()
    db_session.commit()
    return text


@pytest.fixture
def user_factory(db_session):
    def create_user(email: str = "user@example.com") -> User:
        user = User(
            email=email,
            password_hash="test-password-hash",
        )
        db_session.add(user)
        db_session.flush()
        return user

    return create_user


@pytest.fixture
def dictionary_entry_factory(db_session):
    def create_dictionary_entry(
        lemma: str = "reduce",
        translations: tuple[str, ...] = ("уменьшать",),
        definitions: tuple[str, ...] = ("To make something smaller.",),
        pronunciations: tuple[str, ...] = ("/rɪˈdjuːs/",),
        part_of_speech: str = "verb",
    ):
        unique_suffix = uuid4().hex
        source = DictionarySource(
            name=f"test-source-{unique_suffix}",
            version="1",
            license_name="test",
            license_url="https://example.com/license",
            source_url="https://example.com/dictionary",
            content_sha256="a" * 64,
        )
        db_session.add(source)
        db_session.flush()

        lexeme = Lexeme(
            source_id=source.id,
            lemma=lemma,
            normalized_lemma=lemma.casefold(),
            part_of_speech=part_of_speech,
        )
        db_session.add(lexeme)
        db_session.flush()

        sense = SourceSense(
            lexeme_id=lexeme.id,
            source_order=1,
        )
        db_session.add(sense)
        db_session.flush()

        translation_models = []
        for source_order, translation_text in enumerate(translations, start=1):
            translation = Translation(
                sense_id=sense.id,
                language="ru",
                source_order=source_order,
                text=translation_text,
                normalized_text=translation_text.casefold(),
            )
            db_session.add(translation)
            translation_models.append(translation)

        definition_models = []
        for source_order, definition_text in enumerate(definitions, start=1):
            definition = Definition(
                sense_id=sense.id,
                language="en",
                source_order=source_order,
                text=definition_text,
                text_sha256=str(source_order) * 64,
            )
            db_session.add(definition)
            definition_models.append(definition)

        pronunciation_models = []
        for source_order, pronunciation_text in enumerate(
            pronunciations,
            start=1,
        ):
            pronunciation = Pronunciation(
                lexeme_id=lexeme.id,
                text=pronunciation_text,
                source_order=source_order,
            )
            db_session.add(pronunciation)
            pronunciation_models.append(pronunciation)

        db_session.flush()

        return {
            "source": source,
            "lexeme": lexeme,
            "sense": sense,
            "translations": translation_models,
            "definitions": definition_models,
            "pronunciations": pronunciation_models,
        }

    return create_dictionary_entry
