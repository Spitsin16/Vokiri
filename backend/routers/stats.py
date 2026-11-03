from fastapi import APIRouter, Depends
from backend.database import get_db
from backend.dependencies import get_current_user
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.service.stats_service import Stats 

router = APIRouter(prefix="/stats",tags=["stats"])

@router.get("/get_all_words_count")
def get_all_words_count(db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    service = Stats(db)

    return service.all_words_in_vocablury_count(current_user.id)

@router.get("/get_current_streak")
def get_current_streak(db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = Stats(db)
    return service.get_current_streak(current_user.id)

@router.get("/get_max_streak")
def get_max_streak(db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = Stats(db)
    return service.get_max_streak(current_user.id)