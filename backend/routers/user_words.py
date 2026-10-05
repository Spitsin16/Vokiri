from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas.user import AddWord, DeleteWordResponse
from backend.models.user import User
from backend.service.user_word_service import UserWordService

router = APIRouter(prefix="/user_words",tags=["user_words"])

@router.post("/add",status_code=201)
def add_word(data: AddWord, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    service = UserWordService(db)

    try:
        return service.add_word(current_user.id, data.sense_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Meaning not found")
    except ValueError:
        raise HTTPException(status_code=409, detail="Word already in dictionary")

@router.get("/get_all_words")
def get_words(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    service = UserWordService(db)

    return service.get_all_words(current_user.id)
    
@router.delete("/delete_word", response_model=DeleteWordResponse)
def delete_word(data: AddWord,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    service = UserWordService(db)

    try:
        return service.delete_word(current_user.id, data.sense_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Meaning not found in your dictionary")
    
