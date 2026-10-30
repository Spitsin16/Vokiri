import pytest
from sqlalchemy import select

from backend.models.text import UserText, AllText
from backend.models.user import User

def test_get_all_texts_returns_user_texts(client, authenticated_user, db_session):

    user = db_session.scalar(select(User).where(User.email==authenticated_user["email"]))

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

    user_text = UserText(user_id=user.id,
                         text_id=text.id)

    db_session.add(user_text)
    db_session.commit()

    response = client.get("/user_texts/get_all",headers=authenticated_user["headers"])

    assert response.status_code == 200
    assert response.json() == [{"title" : "Football story",
                              "id": text.id}]

def test_get_all_texts_returns_empty_list(
    client,
    authenticated_user,
):
    response = client.get(
        "/user_texts/get_all",
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []

def test_get_all_texts_requires_authentication(client):
    response = client.get("/user_texts/get_all")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }