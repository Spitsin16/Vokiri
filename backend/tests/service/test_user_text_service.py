import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from backend.exceptions.exceptions_classes import NotFoundError
from backend.models.text import AllText, UserText
from backend.service.user_text_service import UserTextService


def create_text(db_session: Session, title: str) -> AllText:
    text = AllText(
        title=title,
        theme="Testing",
        level="B1",
        target_words=[],
        word_count=2,
        content=f"{title} content",
    )
    db_session.add(text)
    db_session.flush()
    return text


def test_get_all_texts_returns_only_requested_user_texts(
    db_session: Session,
    user_factory,
):
    first_user = user_factory("first-text@example.com")
    second_user = user_factory("second-text@example.com")
    first_text = create_text(db_session, "First")
    second_text = create_text(db_session, "Second")
    db_session.add_all(
        [
            UserText(user_id=first_user.id, text_id=first_text.id),
            UserText(user_id=second_user.id, text_id=second_text.id),
        ]
    )
    db_session.flush()
    service = UserTextService(db_session)

    result = service.get_all_texts(first_user.id)

    assert result == [{"title": "First", "id": first_text.id}]


def test_get_all_texts_returns_empty_list(
    db_session: Session,
    user_factory,
):
    user = user_factory("empty-texts@example.com")
    service = UserTextService(db_session)

    assert service.get_all_texts(user.id) == []


def test_get_all_texts_uses_single_database_query(
    db_session: Session,
    user_factory,
):
    user = user_factory("query-count-texts@example.com")
    first_text = create_text(db_session, "First query")
    second_text = create_text(db_session, "Second query")
    db_session.add_all(
        [
            UserText(user_id=user.id, text_id=first_text.id),
            UserText(user_id=user.id, text_id=second_text.id),
        ]
    )
    db_session.commit()
    user_id = user.id
    query_count = 0

    def count_query(*_args):
        nonlocal query_count
        query_count += 1

    event.listen(db_session.bind, "before_cursor_execute", count_query)
    try:
        result = UserTextService(db_session).get_all_texts(user_id)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", count_query)

    assert len(result) == 2
    assert query_count == 1


def test_get_certain_text_returns_owned_text(
    db_session: Session,
    user_factory,
):
    user = user_factory("owner@example.com")
    text = create_text(db_session, "Owned")
    db_session.add(UserText(user_id=user.id, text_id=text.id))
    db_session.flush()
    service = UserTextService(db_session)

    result = service.get_certain_text(text.id, user.id)

    assert result == {
        "title": "Owned",
        "content": "Owned content",
    }


def test_get_certain_text_rejects_another_users_text(
    db_session: Session,
    user_factory,
):
    owner = user_factory("text-owner@example.com")
    other_user = user_factory("other-user@example.com")
    text = create_text(db_session, "Private")
    db_session.add(UserText(user_id=owner.id, text_id=text.id))
    db_session.flush()
    service = UserTextService(db_session)

    with pytest.raises(NotFoundError, match="Wrong text id"):
        service.get_certain_text(text.id, other_user.id)


def test_get_certain_text_rejects_unknown_text(
    db_session: Session,
    user_factory,
):
    user = user_factory("unknown-text@example.com")
    service = UserTextService(db_session)

    with pytest.raises(NotFoundError, match="Wrong text id"):
        service.get_certain_text(999999, user.id)
