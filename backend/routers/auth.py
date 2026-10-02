from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_db
from backend.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from sqlalchemy.orm import Session


from backend.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register",status_code=201, response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        return service.register_user(user_data.email, user_data.password)
    except ValueError:
        raise HTTPException(status_code=409, detail="Email already registered")

@router.post("/login",response_model=TokenResponse)
def login(user_data:UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        return service.login(user_data.email, user_data.password)
    except ValueError :
        raise HTTPException(status_code=401, detail="Wrong email or password")