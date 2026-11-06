from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.activity import DailyActivity
from backend.models.user import User
from backend.service.stats_service import Stats
from backend.utils.dates import moscow_today


def create_user(db_session: Session, email: str) -> User:
    user = User(
        email=email,
        password_hash="test-password-hash",
    )
    db_session.add(user)
    db_session.flush()
    return user


def add_activity_dates(
    db_session: Session,
    user_id: int,
    activity_dates: list[date],
):
    db_session.add_all(
        [
            DailyActivity(
                user_id=user_id,
                activity_date=activity_date,
                reviewed_cards=1,
            )
            for activity_date in activity_dates
        ]
    )
    db_session.flush()


def test_record_review_creates_today_activity(db_session: Session):
    user = create_user(db_session, "first@example.com")
    service = Stats(db_session)

    service.record_review(user.id)
    db_session.flush()

    activity = db_session.scalar(
        select(DailyActivity).where(
            DailyActivity.user_id == user.id,
            DailyActivity.activity_date == moscow_today(),
        )
    )

    assert activity is not None
    assert activity.reviewed_cards == 1


def test_record_review_increments_existing_activity(db_session: Session):
    user = create_user(db_session, "second@example.com")
    service = Stats(db_session)

    service.record_review(user.id)
    db_session.flush()
    service.record_review(user.id)
    db_session.flush()

    activity = db_session.scalar(
        select(DailyActivity).where(
            DailyActivity.user_id == user.id,
            DailyActivity.activity_date == moscow_today(),
        )
    )
    activity_count = db_session.scalar(
        select(func.count(DailyActivity.id)).where(
            DailyActivity.user_id == user.id,
        )
    )

    assert activity.reviewed_cards == 2
    assert activity_count == 1


def test_current_streak_can_end_yesterday(db_session: Session):
    user = create_user(db_session, "third@example.com")
    today = moscow_today()
    add_activity_dates(
        db_session,
        user.id,
        [
            today - timedelta(days=2),
            today - timedelta(days=1),
        ],
    )

    service = Stats(db_session)

    assert service.get_current_streak(user.id) == 2


def test_expired_streak_does_not_remove_historical_max(db_session: Session):
    user = create_user(db_session, "fourth@example.com")
    today = moscow_today()
    add_activity_dates(
        db_session,
        user.id,
        [
            today - timedelta(days=5),
            today - timedelta(days=4),
            today - timedelta(days=3),
        ],
    )

    service = Stats(db_session)

    assert service.get_current_streak(user.id) == 0
    assert service.get_max_streak(user.id) == 3


def test_streaks_use_only_requested_user_activity(db_session: Session):
    first_user = create_user(db_session, "fifth@example.com")
    second_user = create_user(db_session, "sixth@example.com")
    today = moscow_today()
    add_activity_dates(db_session, first_user.id, [today])
    add_activity_dates(
        db_session,
        second_user.id,
        [
            today - timedelta(days=2),
            today - timedelta(days=1),
            today,
        ],
    )

    service = Stats(db_session)

    assert service.get_current_streak(first_user.id) == 1
    assert service.get_max_streak(first_user.id) == 1
