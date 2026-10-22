from backend.utils.tokens import create_access_token
from backend.models.user import User
from sqlalchemy import select

def test_success_get_current_user(client,authenticated_user):
    response = client.get("/auth/me",headers = authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json()["email"] == authenticated_user["email"]
    assert response.json()["is_active"] is True

def test_me_rejects_request_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401

def test_absolute_wrong_token_get_current_user(client,authenticated_user):
    response = client.get("/auth/me",headers = {"Authorization":"Bearer wrong-token"})
    assert response.status_code == 401

def test_wrong_id_token_get_current_user(client,authenticated_user):
    token = create_access_token(2387)
    response = client.get("/auth/me",headers = {"Authorization":f"Bearer {token}"})
    assert response.status_code == 401

def test_is_active_user_false(db_session, authenticated_user,client):
    user = db_session.scalar(select(User).where(User.email==authenticated_user["email"]))
    user.is_active = False
    db_session.commit()
    response = client.get("/auth/me", headers = authenticated_user["headers"])

    assert response.status_code == 401
