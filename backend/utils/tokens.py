from datetime import datetime, timedelta, timezone
import jwt
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, SECRET_KEY

def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": str(user_id),
               "exp": expires_at}
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

    return payload

