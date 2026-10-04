from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_db
from backend.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from sqlalchemy.orm import Session
from backend.dependencies import get_current_user
from backend.service.auth_service import AuthService
from backend.models.user import User 

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

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user