from fastapi import APIRouter, Depends
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.service.user_text_service import UserTextService
router = APIRouter(prefix="/user_texts",tags=["text"])

@router.get("/get_all")
def get_all_texts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    service = UserTextService(db) 
    return service.get_all_texts(current_user.id)

@router.get("/get_current")
def get_current_text(text_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    service = UserTextService(db) 
    return service.get_certain_text(text_id,current_user.id)