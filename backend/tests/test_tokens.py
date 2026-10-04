from backend.tokens import create_access_token, decode_access_token
import pytest
import jwt

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