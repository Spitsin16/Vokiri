from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.user import User
from backend.utils.passwords import hash_password, verify_password
from backend.tokens import create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, email: str, password: str ) -> User:
        normalized_email = email.strip().casefold()

        existing_user = self.db.scalar(select(User).where(User.email == normalized_email))

        if existing_user is not None:
            raise ValueError("Email already registered")
        
        hashed_password = hash_password(password)

        new_user = User(
            email = normalized_email,
            password_hash = hashed_password)
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user
    
    def login(self, email: str, password: str):
        normalized_email = email.strip().casefold()

        user = self.db.scalar(select(User).where(User.email == normalized_email))

        if user is None:
            raise ValueError("Wrong email or password")
        
        password_is_valid = verify_password(password, user.password_hash)

        if password_is_valid is False:
            raise ValueError("Wrong email or password")
        
        token = create_access_token(user.id)

        return {
        "access_token": token,
        "token_type": "bearer",
    }


        
        


