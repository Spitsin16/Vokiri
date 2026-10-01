from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_db
from backend.schemas.user import UserCreate, UserResponse, UserLogin
from backend.models.user import User
from backend.passwords import hash_password, verify_password
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register",status_code=201, response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    normalized_email = user_data.email.strip().casefold()

    existing_user = db.scalar(select(User).where(User.email==normalized_email))

    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email = normalized_email,
        password_hash = hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(user_data:UserLogin, db: Session = Depends(get_db)):
    normalized_email = user_data.email.strip().casefold()
    

    user=db.scalar(select(User).where(User.email==normalized_email))

    if user is None:
        raise HTTPException(status_code=401, detail="Wrong email or password")

    password_is_valid = verify_password(user_data.password, user.password_hash)

    if password_is_valid is False:
        raise HTTPException(status_code=401, detail="Wrong email or password")

    return {
        "message": "Login successful",
        "user_id": user.id,
    }

