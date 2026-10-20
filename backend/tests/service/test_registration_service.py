from sqlalchemy import select
from sqlalchemy.orm import Session
import pytest
from backend.models.user import User
from backend.service.auth_service import AuthService
from backend.utils.passwords import verify_password
from backend.exceptions.exceptions_classes import AuthenticationError, ConflictError


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

    with pytest.raises(ConflictError):
        service.register_user("user@mail.com", password)



