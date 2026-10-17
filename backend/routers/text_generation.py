from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas.text import TextCreate, ResponseText
from backend.models.user import User
from backend.service.ai_integration import AiIntegration

router = APIRouter(prefix="/text",tags=["text"])

@router.post("/create",response_model=ResponseText)
def create_text(data: TextCreate, db: Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AiIntegration(db)

    return service.generate_text(data.level, data.min_words,data.max_words, data.theme)
