from backend.utils.tokens import create_access_token, decode_access_token
import pytest
import jwt
from backend.config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timezone, timedelta
def test_check_correct_token():
    user_id = 15
    token = create_access_token(15)

    payload = decode_access_token(token)

    assert str(user_id) == payload['sub']
    assert "exp" in payload

def test_check_wrong_token():
    wrong_token = "wrong-token-"

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(wrong_token)

def test_expire_token():
    payload = {"sub": 30,
               "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)

def wrong_signature():
    payload = {"sub": 30,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(payload, "dfjdfd ", algorithm=JWT_ALGORITHM)

    with pytest.raises(jwt.ImmatureSignatureError):
        decode_access_token(token) 
