from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.dependencies import get_current_user
from backend.service.user_word_service import UserWordService
from backend.schemas.user import GetAllWordsResponse
from backend.schemas.review import ReviewAnswer

router = APIRouter(prefix="/review", tags=["review"])

@router.get("/today",response_model=list[GetAllWordsResponse])
def get_today_review(limit: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = UserWordService(db)

    return service.get_today_cards(current_user.id, limit)
@router.post("/{user_word_id}/answer")
def answer_card(data: ReviewAnswer, user_word_id:int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = UserWordService(db)

    return service.answer_card(current_user.id, user_word_id,data.answer)