from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from httpx import HTTPError
from sqlalchemy import func, select
from sqlalchemy.orm import Session
import pytest

from backend.config import AI_DAILY_GENERATION_LIMIT
from backend.exceptions.exceptions_classes import AiServiceError, RateLimitError
from backend.models.text import AllText, UserText
from backend.service.ai_integration import AiIntegration
from backend.service.user_word_service import UserWordService

def test_generation_allowed_when_user_has_no_recent_texts(db_session):
    service = AiIntegration(db_session)
    service.check_generated_limit(user_id=1)

def test_generation_rejected_when_limit_reached(db_session):
    user_id = 1

    for number in range(AI_DAILY_GENERATION_LIMIT):
        text = AllText(
            title=f"Text {number}",
            theme="Football",
            level="B1",
            target_words=[],
            word_count=100,
            content="Test content",
        )

        db_session.add(text)
        db_session.flush()

        user_text = UserText(
            user_id=user_id,
            text_id=text.id,
        )
        db_session.add(user_text)

    db_session.commit()

    service = AiIntegration(db_session)

    with pytest.raises(RateLimitError):
        service.check_generated_limit(user_id)


def test_old_and_another_users_texts_do_not_use_limit(db_session):
    user_id = 1

    for number in range(AI_DAILY_GENERATION_LIMIT):
        text = AllText(
            title=f"Old text {number}",
            theme="History",
            level="B1",
            target_words=[],
            word_count=100,
            content="Old content",
            created_at=datetime.now(timezone.utc) - timedelta(hours=25),
        )
        db_session.add(text)
        db_session.flush()
        db_session.add(UserText(user_id=user_id, text_id=text.id))

    another_users_text = AllText(
        title="Another user's text",
        theme="History",
        level="B1",
        target_words=[],
        word_count=100,
        content="Recent content",
    )
    db_session.add(another_users_text)
    db_session.flush()
    db_session.add(UserText(user_id=999, text_id=another_users_text.id))
    db_session.commit()

    service = AiIntegration(db_session)

    service.check_generated_limit(user_id)


def configure_gigachat_response(monkeypatch, raw_response: str):
    client = MagicMock()
    client.chat.create.return_value = SimpleNamespace(
        messages=[
            SimpleNamespace(
                content=[SimpleNamespace(text=raw_response)],
            )
        ]
    )
    gigachat = MagicMock()
    gigachat.return_value.__enter__.return_value = client
    monkeypatch.setattr(
        "backend.service.ai_integration.GigaChat",
        gigachat,
    )
    return client


def test_generate_text_saves_generated_text_and_user_relation(
    db_session: Session,
    user_factory,
    monkeypatch,
):
    user = user_factory("ai-success@example.com")
    target_words = [
        {"word": "reduce", "translation": "уменьшать"},
        {"word": "achieve", "translation": "достигать"},
    ]
    monkeypatch.setattr(
        UserWordService,
        "get_today_cards",
        lambda self, user_id, limit: target_words,
    )
    client = configure_gigachat_response(
        monkeypatch,
        '{"title":"A Better City","text":"We reduce waste and achieve progress."}',
    )
    service = AiIntegration(db_session)

    result = service.generate_text(
        level="B1",
        min_words=50,
        max_words=100,
        theme="Sustainable city",
        user_id=user.id,
        limit_words=2,
    )

    saved_text = db_session.scalar(select(AllText))
    saved_relation = db_session.scalar(select(UserText))
    prompt = client.chat.create.call_args.args[0]

    assert result.title == "A Better City"
    assert result.text == "We reduce waste and achieve progress."
    assert saved_text.title == result.title
    assert saved_text.content == result.text
    assert saved_text.target_words == target_words
    assert saved_text.word_count == 6
    assert saved_relation.user_id == user.id
    assert saved_relation.text_id == saved_text.id
    assert "reduce" in prompt
    assert "achieve" in prompt
    assert "Sustainable city" in prompt


def test_generate_text_converts_invalid_ai_response_to_service_error(
    db_session: Session,
    user_factory,
    monkeypatch,
):
    user = user_factory("ai-invalid@example.com")
    monkeypatch.setattr(
        UserWordService,
        "get_today_cards",
        lambda self, user_id, limit: [],
    )
    configure_gigachat_response(monkeypatch, "invalid response")
    service = AiIntegration(db_session)

    with pytest.raises(AiServiceError, match="invalid response"):
        service.generate_text("B1", 50, 100, "History", user.id, 5)

    assert db_session.scalar(select(func.count(AllText.id))) == 0
    assert db_session.scalar(select(func.count(UserText.id))) == 0


def test_generate_text_converts_network_error_to_service_error(
    db_session: Session,
    user_factory,
    monkeypatch,
):
    user = user_factory("ai-network@example.com")
    monkeypatch.setattr(
        UserWordService,
        "get_today_cards",
        lambda self, user_id, limit: [],
    )
    gigachat = MagicMock()
    client = gigachat.return_value.__enter__.return_value
    client.chat.create.side_effect = HTTPError("connection failed")
    monkeypatch.setattr(
        "backend.service.ai_integration.GigaChat",
        gigachat,
    )
    service = AiIntegration(db_session)

    with pytest.raises(AiServiceError, match="unavailable"):
        service.generate_text("B1", 50, 100, "History", user.id, 5)

    assert db_session.scalar(select(func.count(AllText.id))) == 0
    assert db_session.scalar(select(func.count(UserText.id))) == 0


def test_generate_text_checks_limit_before_calling_gigachat(
    db_session: Session,
    user_factory,
    monkeypatch,
):
    user = user_factory("ai-limit@example.com")
    for number in range(AI_DAILY_GENERATION_LIMIT):
        text = AllText(
            title=f"Recent {number}",
            theme="History",
            level="B1",
            target_words=[],
            word_count=100,
            content="Recent content",
        )
        db_session.add(text)
        db_session.flush()
        db_session.add(UserText(user_id=user.id, text_id=text.id))
    db_session.commit()
    gigachat = MagicMock()
    monkeypatch.setattr(
        "backend.service.ai_integration.GigaChat",
        gigachat,
    )
    service = AiIntegration(db_session)

    with pytest.raises(RateLimitError):
        service.generate_text("B1", 50, 100, "History", user.id, 5)

    gigachat.assert_not_called()
