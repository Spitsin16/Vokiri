import pytest

from backend.service.dictionary_service import DictionaryService
from sqlalchemy.orm import Session


def test_mixed_word(db_session: Session):
    service = DictionaryService(db_session)

    with pytest.raises(LookupError):
        service.lookup_word("assф")
