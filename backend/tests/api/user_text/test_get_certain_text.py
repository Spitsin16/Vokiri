from sqlalchemy import select

from backend.models.text import UserText, AllText
from backend.models.user import User

def test_success_get_certain_text(client, db_session, authenticated_user,create_text):
    user = db_session.scalar(select(User).where(User.email == authenticated_user["email"]))

    user_text = UserText(user_id = user.id, text_id = create_text.id)
    db_session.add(user_text)
    db_session.commit()

    response = client.get("/user_texts/get_current", params= {"text_id":create_text.id},headers=authenticated_user["headers"])

    assert response.status_code == 200 
    assert response.json() == {
        "title": "Football story",
        "content": "Test English text.",
    }

def test_wrong_text_id_get_certain_text(client, db_session, authenticated_user,create_text):
    user = db_session.scalar(select(User).where(User.email == authenticated_user["email"]))

    user_text = UserText(user_id = user.id, text_id = create_text.id)
    db_session.add(user_text)
    db_session.commit()

    response = client.get("/user_texts/get_current", params= {"text_id":create_text.id+1},headers=authenticated_user["headers"])

    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong text id"}

def test_get_current_text_rejects_text_not_owned_by_user(client,authenticated_user, create_text):
    response = client.get("/user_texts/get_current", params= {"text_id":create_text.id},headers=authenticated_user["headers"])

    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong text id"}

def test_get_current_text_requires_authentication(client):
    response = client.get(
        "/user_texts/get_current",
        params={"text_id": 1},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }

def test_get_current_text_requires_text_id(
    client,
    authenticated_user,
):
    response = client.get(
        "/user_texts/get_current",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 422

def test_text_another_user(client, db_session, authenticated_user,create_text):
    user1 = db_session.scalar(select(User).where(User.email==authenticated_user["email"]))

    email = "test123@mail.com"
    password = "qwerty12341234"
    register_response = client.post("/auth/register", json = {"email": email,
                                          "password": password})
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json = {"email": email,
                                          "password": password})
    assert login_response.status_code == 200

    body = login_response.json()
    token = body["access_token"]
    user2 = db_session.scalar(select(User).where(User.email==email))

    user_text1 = UserText(user_id = user1.id, text_id = create_text.id)
    db_session.add(user_text1)

    text = AllText(
        title="Football story",
        theme="Football",
        level="B1",
        target_words=[
            {
                "word": "achieve",
                "translation": "достигать",
            }
        ],
        word_count=100,
        content="Test English text.",
    )
    db_session.add(text)
    db_session.flush()
    user_text2 = UserText(user_id = user2.id, text_id = text.id)
    db_session.add(user_text2)
    db_session.commit()

    response = client.get(
        "/user_texts/get_current",
        params = {"text_id": user_text2.id},
        headers=authenticated_user["headers"],
    )

    assert response.status_code==404
    assert response.json() == {
        "detail": "Wrong text id"
    }




