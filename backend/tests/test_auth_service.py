from sqlalchemy import select
from sqlalchemy.orm import Session
import pytest

from backend.models.user import User
from backend.service.auth_service import AuthService
from backend.utils.passwords import verify_password

def test_register_user(db_session: Session):
    password="StrongPassword123!"

    service = AuthService(db_session)

    user = service.register_user(" User@Example.com ",password)

    user_from_database = db_session.scalar(select(User).where(User.id==user.id))

    assert user.id is not None
    assert user_from_database.password_hash != password
    assert verify_password(password, user_from_database.password_hash) is True

def test_register_with_duplicate_email(db_session: Session):
    password="StrongPassword123!"

    service = AuthService(db_session)

    service.register_user("user@mail.com", password)

    with pytest.raises(ValueError):
        service.register_user("user@mail.com", password)

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

    with pytest.raises(ValueError):
        service.login("use@mail.com", password)

def test_login_rejects_wrong_password(db_session: Session):
    password="StrongPassword123!"
    wrong_password="StronPassword123!"

    service = AuthService(db_session)

    service.register_user("user@mail.com", password)

    with pytest.raises(ValueError):
        service.login("user@mail.com", wrong_password)



    




