from datetime import date, timedelta

import pytest
from sqlalchemy import select

from backend.models.activity import DailyActivity
from backend.models.dictionary import DictionarySource, Lexeme, SourceSense
from backend.models.user import User
from backend.models.user_word import UserWord


def get_authenticated_user_id(db_session, authenticated_user) -> int:
    user = db_session.scalar(
        select(User).where(User.email == authenticated_user["email"])
    )
    return user.id


def add_activity_dates(db_session, user_id: int, activity_dates: list[date]):
    for activity_date in activity_dates:
        db_session.add(
            DailyActivity(
                user_id=user_id,
                activity_date=activity_date,
                reviewed_cards=1,
            )
        )
    db_session.commit()


def test_words_count_returns_only_active_words(
    client,
    authenticated_user,
    db_session,
):
    user_id = get_authenticated_user_id(db_session, authenticated_user)

    source = DictionarySource(
        name="test",
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
        lemma="test",
        normalized_lemma="test",
        part_of_speech="noun",
    )
    db_session.add(lexeme)
    db_session.flush()

    active_sense = SourceSense(lexeme_id=lexeme.id, source_order=1)
    inactive_sense = SourceSense(lexeme_id=lexeme.id, source_order=2)
    db_session.add_all([active_sense, inactive_sense])
    db_session.flush()

    db_session.add_all(
        [
            UserWord(
                user_id=user_id,
                source_sense_id=active_sense.id,
                is_active=True,
            ),
            UserWord(
                user_id=user_id,
                source_sense_id=inactive_sense.id,
                is_active=False,
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        "/stats/get_all_words_count",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == {"Words in vocablury": 1}


def test_current_streak_returns_zero_without_activity(
    client,
    authenticated_user,
):
    response = client.get(
        "/stats/get_current_streak",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == 0


def test_current_streak_returns_latest_consecutive_days(
    client,
    authenticated_user,
    db_session,
):
    user_id = get_authenticated_user_id(db_session, authenticated_user)
    today = date.today()
    add_activity_dates(
        db_session,
        user_id,
        [
            today - timedelta(days=5),
            today - timedelta(days=4),
            today - timedelta(days=2),
            today - timedelta(days=1),
            today,
        ],
    )

    response = client.get(
        "/stats/get_current_streak",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == 3


def test_current_streak_returns_zero_when_streak_expired(
    client,
    authenticated_user,
    db_session,
):
    user_id = get_authenticated_user_id(db_session, authenticated_user)
    today = date.today()
    add_activity_dates(
        db_session,
        user_id,
        [
            today - timedelta(days=4),
            today - timedelta(days=3),
        ],
    )

    response = client.get(
        "/stats/get_current_streak",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == 0


def test_max_streak_returns_longest_sequence(
    client,
    authenticated_user,
    db_session,
):
    user_id = get_authenticated_user_id(db_session, authenticated_user)
    today = date.today()
    add_activity_dates(
        db_session,
        user_id,
        [
            today - timedelta(days=10),
            today - timedelta(days=9),
            today - timedelta(days=8),
            today - timedelta(days=7),
            today - timedelta(days=1),
            today,
        ],
    )

    response = client.get(
        "/stats/get_max_streak",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == 4


@pytest.mark.parametrize(
    "path",
    [
        "/stats/get_all_words_count",
        "/stats/get_current_streak",
        "/stats/get_max_streak",
    ],
)
def test_stats_endpoints_require_authentication(client, path):
    response = client.get(path)

    assert response.status_code == 401
