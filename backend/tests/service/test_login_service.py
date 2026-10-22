from backend.service.auth_service import AuthService
from sqlalchemy.orm import Session
from backend.exceptions.exceptions_classes import AuthenticationError
import pytest

def test_success_login(db_session: Session):
    password="StrongPassword123!"

    service = AuthService(db_session)

    service.register_user("user@mail.com", password)
    result = service.login("user@mail.com", password)

    assert result["token_type"] == "bearer"
    assert result["access_token"] != ""
    assert isinstance(result["access_token"], str)


def test_login_rejects_unknown_email(db_session: Session):
    password="StrongPassword123!"
    
    service = AuthService(db_session)

    service.register_user("user@mail.com", password)

    with pytest.raises(AuthenticationError):
        service.login("use@mail.com", password)

def test_login_rejects_wrong_password(db_session: Session):
    password="StrongPassword123!"
    wrong_password="StronPassword123!"

    service = AuthService(db_session)

    service.register_user("user@mail.com", password)

    with pytest.raises(AuthenticationError):
        service.login("user@mail.com", wrong_password)


