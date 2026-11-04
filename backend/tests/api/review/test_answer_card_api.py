from datetime import date

from sqlalchemy import func, select

from backend.models.activity import DailyActivity
from backend.models.dictionary import DictionarySource, Lexeme, SourceSense
from backend.models.user import User
from backend.models.user_word import UserWord


def create_user_word(db_session, authenticated_user) -> UserWord:
    user = db_session.scalar(
        select(User).where(User.email == authenticated_user["email"])
    )

    source = DictionarySource(
        name="review-test",
        version="1",
        license_name="test",
        license_url="https://example.com/license",
        source_url="https://example.com/dictionary",
        content_sha256="b" * 64,
    )
    db_session.add(source)
    db_session.flush()

    lexeme = Lexeme(
        source_id=source.id,
        lemma="review",
        normalized_lemma="review",
        part_of_speech="verb",
    )
    db_session.add(lexeme)
    db_session.flush()

    sense = SourceSense(
        lexeme_id=lexeme.id,
        source_order=1,
    )
    db_session.add(sense)
    db_session.flush()

    word = UserWord(
        user_id=user.id,
        source_sense_id=sense.id,
        is_active=True,
    )
    db_session.add(word)
    db_session.commit()
    db_session.refresh(word)
    return word


def test_answer_card_creates_and_increments_daily_activity(
    client,
    authenticated_user,
    db_session,
):
    word = create_user_word(db_session, authenticated_user)

    first_response = client.post(
        f"/review/{word.id}/answer",
        json={"answer": "good"},
        headers=authenticated_user["headers"],
    )
    second_response = client.post(
        f"/review/{word.id}/answer",
        json={"answer": "hard"},
        headers=authenticated_user["headers"],
    )

    activities = db_session.scalars(
        select(DailyActivity).where(
            DailyActivity.user_id == word.user_id,
            DailyActivity.activity_date == date.today(),
        )
    ).all()

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(activities) == 1
    assert activities[0].reviewed_cards == 2


def test_invalid_answer_does_not_create_activity(
    client,
    authenticated_user,
    db_session,
):
    word = create_user_word(db_session, authenticated_user)

    response = client.post(
        f"/review/{word.id}/answer",
        json={"answer": "unknown"},
        headers=authenticated_user["headers"],
    )
    activity_count = db_session.scalar(
        select(func.count(DailyActivity.id)).where(
            DailyActivity.user_id == word.user_id,
        )
    )

    assert response.status_code == 422
    assert activity_count == 0


def test_missing_word_does_not_create_activity(
    client,
    authenticated_user,
    db_session,
):
    user = db_session.scalar(
        select(User).where(User.email == authenticated_user["email"])
    )

    response = client.post(
        "/review/999999/answer",
        json={"answer": "good"},
        headers=authenticated_user["headers"],
    )
    activity_count = db_session.scalar(
        select(func.count(DailyActivity.id)).where(
            DailyActivity.user_id == user.id,
        )
    )

    assert response.status_code == 404
    assert activity_count == 0


def test_answer_card_requires_authentication(client):
    response = client.post(
        "/review/1/answer",
        json={"answer": "good"},
    )

    assert response.status_code == 401
