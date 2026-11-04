import pytest
from sqlalchemy.orm import Session

from backend.service.dictionary_service import DictionaryService


def test_lookup_english_word_returns_dictionary_data(
    db_session: Session,
    dictionary_entry_factory,
):
    entry = dictionary_entry_factory(
        lemma="reduce",
        translations=("уменьшать", "сокращать"),
        definitions=("To make something smaller.",),
        pronunciations=("/rɪˈdjuːs/",),
    )
    service = DictionaryService(db_session)

    result = service.lookup_word("  REDUCE  ")

    assert result == {
        "id": entry["lexeme"].id,
        "word": "reduce",
        "part_of_speech": "verb",
        "pronunciations": ["/rɪˈdjuːs/"],
        "meanings": [
            {
                "sense_id": entry["sense"].id,
                "order": 1,
                "translations": [
                    {
                        "text": "уменьшать",
                        "id": entry["translations"][0].id,
                    },
                    {
                        "text": "сокращать",
                        "id": entry["translations"][1].id,
                    },
                ],
                "definitions": ["To make something smaller."],
            }
        ],
    }


def test_lookup_russian_word_returns_matching_english_word(
    db_session: Session,
    dictionary_entry_factory,
):
    entry = dictionary_entry_factory(
        lemma="reduce",
        translations=("уменьшать",),
    )
    service = DictionaryService(db_session)

    result = service.lookup_word(" УМЕНЬШАТЬ ")

    assert result["query"] == " УМЕНЬШАТЬ "
    assert result["language"] == "ru"
    assert result["results"] == [
        {
            "lexeme_id": entry["lexeme"].id,
            "word": "reduce",
            "part_of_speech": "verb",
            "sense_id": entry["sense"].id,
            "translation": {
                "id": entry["translations"][0].id,
                "text": "уменьшать",
            },
        }
    ]


@pytest.mark.parametrize("word", ["unknown", "неизвестное"])
def test_lookup_rejects_unknown_word(db_session: Session, word: str):
    service = DictionaryService(db_session)

    with pytest.raises(ValueError, match="Word not found"):
        service.lookup_word(word)


def test_lookup_rejects_mixed_language(db_session: Session):
    service = DictionaryService(db_session)

    with pytest.raises(LookupError, match="single language"):
        service.lookup_word("redслово")


def test_search_english_words_returns_ordered_matches(
    db_session: Session,
    dictionary_entry_factory,
):
    dictionary_entry_factory(lemma="realize")
    dictionary_entry_factory(lemma="reduce")
    dictionary_entry_factory(lemma="remember")
    dictionary_entry_factory(lemma="other")
    service = DictionaryService(db_session)

    result = service.search(" Re ")

    assert result == {
        "query": " Re ",
        "results": ["realize", "reduce", "remember"],
    }


def test_search_russian_words_returns_distinct_matches(
    db_session: Session,
    dictionary_entry_factory,
):
    dictionary_entry_factory(lemma="reduce", translations=("уменьшать",))
    dictionary_entry_factory(lemma="decrease", translations=("уменьшение",))
    dictionary_entry_factory(lemma="other", translations=("другой",))
    service = DictionaryService(db_session)

    result = service.search(" умень ")

    assert result == {
        "query": " умень ",
        "results": ["уменьшать", "уменьшение"],
    }


def test_search_rejects_query_shorter_than_two_characters(db_session: Session):
    service = DictionaryService(db_session)

    with pytest.raises(ValueError, match="at least 2"):
        service.search("a")


def test_search_rejects_mixed_language(db_session: Session):
    service = DictionaryService(db_session)

    with pytest.raises(LookupError, match="single language"):
        service.search("reслово")
