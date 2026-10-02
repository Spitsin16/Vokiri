from fastapi import APIRouter, Query, HTTPException, Depends

from sqlalchemy.orm import Session

from backend.database import get_db
from backend.service.dictionary_service import DictionaryService

router = APIRouter(prefix="/dictionary",tags=["dictionary"])

@router.get("/lookup")
def lookup_word(word: str, db: Session=Depends(get_db)):
    service = DictionaryService(db)

    try:
        return service.lookup_word(word)
    except ValueError:
        raise HTTPException(status_code=404, detail="Word not found")

@router.get("/search")
def search(q: str = Query(min_length=2), db: Session=Depends(get_db)):
    service = DictionaryService(db)

    try:
        return service.search(q)
    except ValueError:
        raise HTTPException(status_code=422, detail="Enter at least 2 characters")

