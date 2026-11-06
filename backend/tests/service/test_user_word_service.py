from datetime import timedelta

import pytest
from sqlalchemy import event
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.exceptions.exceptions_classes import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from backend.models.activity import DailyActivity
from backend.models.user_word import UserWord
from backend.service.user_word_service import UserWordService
from backend.utils.dates import moscow_today


def test_add_word_requires_translation_choice(db_session: Session):
    service = UserWordService(db_session)

    with pytest.raises(ValidationError, match="Choose a translation"):
        service.add_word(
            user_id=1,
            sense_id=1,
            translation_id=None,
            custom_translation=None,
        )


def test_add_word_rejects_two_translation_choices(db_session: Session):
    service = UserWordService(db_session)

    with pytest.raises(ValidationError, match="Choose only one"):
        service.add_word(
            user_id=1,
            sense_id=1,
            translation_id=1,
            custom_translation="свой перевод",
        )


def test_add_word_rejects_unknown_sense(
    db_session: Session,
    user_factory,
):
    user = user_factory("unknown-sense@example.com")
    service = UserWordService(db_session)

    with pytest.raises(NotFoundError, match="Meaning not found"):
        service.add_word(
            user_id=user.id,
            sense_id=999999,
            translation_id=None,
            custom_translation="перевод",
        )


def test_add_word_rejects_translation_from_another_sense(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("wrong-translation@example.com")
    first_entry = dictionary_entry_factory(lemma="first")
    second_entry = dictionary_entry_factory(lemma="second")
    service = UserWordService(db_session)

    with pytest.raises(ValidationError, match="does not belong"):
        service.add_word(
            user_id=user.id,
            sense_id=first_entry["sense"].id,
            translation_id=second_entry["translations"][0].id,
            custom_translation=None,
        )


def test_add_word_rejects_blank_custom_translation(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("blank-translation@example.com")
    entry = dictionary_entry_factory(lemma="blank")
    service = UserWordService(db_session)

    with pytest.raises(ValidationError, match="cannot be empty"):
        service.add_word(
            user_id=user.id,
            sense_id=entry["sense"].id,
            translation_id=None,
            custom_translation="   ",
        )


def test_add_word_with_dictionary_translation(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("dictionary-translation@example.com")
    entry = dictionary_entry_factory(lemma="reduce")
    translation = entry["translations"][0]
    service = UserWordService(db_session)

    word = service.add_word(
        user_id=user.id,
        sense_id=entry["sense"].id,
        translation_id=translation.id,
        custom_translation=None,
    )

    assert word.id is not None
    assert word.preferred_translation_id == translation.id
    assert word.custom_translation is None
    assert word.is_active is True


def test_add_word_normalizes_custom_translation(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("custom-translation@example.com")
    entry = dictionary_entry_factory(lemma="custom")
    service = UserWordService(db_session)

    word = service.add_word(
        user_id=user.id,
        sense_id=entry["sense"].id,
        translation_id=None,
        custom_translation="  МОЙ Перевод  ",
    )

    assert word.preferred_translation_id is None
    assert word.custom_translation == "мой перевод"


def test_add_word_rejects_active_duplicate(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("duplicate@example.com")
    entry = dictionary_entry_factory(lemma="duplicate")
    service = UserWordService(db_session)
    service.add_word(
        user.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )

    with pytest.raises(ConflictError, match="already in dictionary"):
        service.add_word(
            user.id,
            entry["sense"].id,
            entry["translations"][0].id,
            None,
        )


def test_add_word_reactivates_deleted_word_with_new_translation(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("reactivate@example.com")
    entry = dictionary_entry_factory(lemma="reactivate")
    service = UserWordService(db_session)
    original_word = service.add_word(
        user.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )
    original_id = original_word.id
    service.delete_word(user.id, entry["sense"].id)

    reactivated_word = service.add_word(
        user.id,
        entry["sense"].id,
        None,
        "новый перевод",
    )

    assert reactivated_word.id == original_id
    assert reactivated_word.is_active is True
    assert reactivated_word.preferred_translation_id is None
    assert reactivated_word.custom_translation == "новый перевод"


def test_get_all_words_returns_active_selected_and_custom_translations(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("all-words@example.com")
    selected_entry = dictionary_entry_factory(
        lemma="selected",
        translations=("выбранный",),
    )
    custom_entry = dictionary_entry_factory(lemma="customword")
    inactive_entry = dictionary_entry_factory(lemma="inactive")
    service = UserWordService(db_session)
    service.add_word(
        user.id,
        selected_entry["sense"].id,
        selected_entry["translations"][0].id,
        None,
    )
    service.add_word(
        user.id,
        custom_entry["sense"].id,
        None,
        "свой",
    )
    service.add_word(
        user.id,
        inactive_entry["sense"].id,
        inactive_entry["translations"][0].id,
        None,
    )
    service.delete_word(user.id, inactive_entry["sense"].id)

    result = service.get_all_words(user.id)
    words_by_lemma = {word["word"]: word for word in result}

    assert set(words_by_lemma) == {"selected", "customword"}
    assert words_by_lemma["selected"]["translation"] == "выбранный"
    assert words_by_lemma["customword"]["translation"] == "свой"


def test_get_all_words_uses_single_database_query(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("query-count-words@example.com")
    first_entry = dictionary_entry_factory(lemma="firstqueryword")
    second_entry = dictionary_entry_factory(lemma="secondqueryword")
    service = UserWordService(db_session)
    service.add_word(
        user.id,
        first_entry["sense"].id,
        first_entry["translations"][0].id,
        None,
    )
    service.add_word(
        user.id,
        second_entry["sense"].id,
        second_entry["translations"][0].id,
        None,
    )
    user_id = user.id
    query_count = 0

    def count_query(*_args):
        nonlocal query_count
        query_count += 1

    event.listen(db_session.bind, "before_cursor_execute", count_query)
    try:
        result = service.get_all_words(user_id)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", count_query)

    assert len(result) == 2
    assert query_count == 1


def test_delete_word_rejects_missing_or_inactive_word(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("delete-errors@example.com")
    entry = dictionary_entry_factory(lemma="delete")
    service = UserWordService(db_session)

    with pytest.raises(NotFoundError):
        service.delete_word(user.id, entry["sense"].id)

    service.add_word(
        user.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )
    service.delete_word(user.id, entry["sense"].id)

    with pytest.raises(NotFoundError):
        service.delete_word(user.id, entry["sense"].id)


def test_get_today_cards_returns_due_and_new_words_only(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("today-cards@example.com")
    due_entry = dictionary_entry_factory(lemma="due")
    new_entry = dictionary_entry_factory(lemma="newword")
    future_entry = dictionary_entry_factory(lemma="future")
    inactive_entry = dictionary_entry_factory(lemma="inactivecard")
    service = UserWordService(db_session)

    due_word = service.add_word(
        user.id,
        due_entry["sense"].id,
        due_entry["translations"][0].id,
        None,
    )
    new_word = service.add_word(
        user.id,
        new_entry["sense"].id,
        new_entry["translations"][0].id,
        None,
    )
    future_word = service.add_word(
        user.id,
        future_entry["sense"].id,
        future_entry["translations"][0].id,
        None,
    )
    inactive_word = service.add_word(
        user.id,
        inactive_entry["sense"].id,
        inactive_entry["translations"][0].id,
        None,
    )
    due_word.next_review_date = moscow_today() - timedelta(days=1)
    new_word.next_review_date = None
    future_word.next_review_date = moscow_today() + timedelta(days=1)
    inactive_word.next_review_date = moscow_today() - timedelta(days=1)
    inactive_word.is_active = False
    db_session.commit()

    result = service.get_today_cards(user.id, limit=10)

    assert [word["word"] for word in result] == ["due", "newword"]


@pytest.mark.parametrize(
    ("answer", "starting_step", "expected_step", "expected_days"),
    [
        ("good", 0, 1, 1),
        ("good", 7, 7, 60),
        ("again", 4, 2, 2),
        ("again", 1, 0, 0),
        ("hard", 4, 3, 4),
        ("hard", 0, 0, 0),
    ],
)
def test_answer_card_updates_review_schedule(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
    answer: str,
    starting_step: int,
    expected_step: int,
    expected_days: int,
):
    user = user_factory(f"answer-{answer}-{starting_step}@example.com")
    entry = dictionary_entry_factory(lemma=f"answer{answer}{starting_step}")
    service = UserWordService(db_session)
    word = service.add_word(
        user.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )
    word.review_step = starting_step
    db_session.commit()

    result = service.answer_card(user.id, word.id, answer)

    assert word.review_step == expected_step
    assert word.next_review_date == moscow_today() + timedelta(days=expected_days)
    assert result["next_show"] == word.next_review_date
    activity = db_session.scalar(
        select(DailyActivity).where(DailyActivity.user_id == user.id)
    )
    assert activity.reviewed_cards == 1


def test_answer_card_rejects_unknown_answer_without_activity(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    user = user_factory("invalid-answer@example.com")
    entry = dictionary_entry_factory(lemma="invalidanswer")
    service = UserWordService(db_session)
    word = service.add_word(
        user.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )

    with pytest.raises(ValidationError, match="Unknown review answer"):
        service.answer_card(user.id, word.id, "unknown")

    activity = db_session.scalar(
        select(DailyActivity).where(DailyActivity.user_id == user.id)
    )
    assert activity is None


def test_answer_card_rejects_another_users_word(
    db_session: Session,
    user_factory,
    dictionary_entry_factory,
):
    owner = user_factory("word-owner@example.com")
    other_user = user_factory("word-other@example.com")
    entry = dictionary_entry_factory(lemma="privateword")
    service = UserWordService(db_session)
    word = service.add_word(
        owner.id,
        entry["sense"].id,
        entry["translations"][0].id,
        None,
    )

    with pytest.raises(NotFoundError, match="Word not found"):
        service.answer_card(other_user.id, word.id, "good")
