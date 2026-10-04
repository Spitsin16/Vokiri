from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.tokens import decode_access_token
from backend.models.user import User
from sqlalchemy import select
import jwt

bearer_scheme = HTTPBearer()

def get_current_user(auth_data: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                     db: Session = Depends(get_db)):
    token = auth_data.credentials
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = db.scalar(select(User).where(User.id==user_id))

    if user is None or user.is_active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not available")

    return user