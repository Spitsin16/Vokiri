from sqlalchemy.orm import Session
from backend.service.ai_integration import AiIntegration
import pytest

from backend.config import AI_DAILY_GENERATION_LIMIT
from backend.exceptions.exceptions_classes import RateLimitError
from backend.models.text import AllText, UserText

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