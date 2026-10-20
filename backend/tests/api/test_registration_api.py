import pytest

@pytest.mark.parametrize("payload", [{"email":"spec@mail",
                                       "password":"dscsdcsdc"},
                                       {"email":"specmail.com",
                                       "password":"dcsdcwdcwdc"},
                                       {"email":"spec@mail.com",
                                       "password":"dcsd"},
                                       {"password":"dcsdcwdcwdc"},
                                       {"email":"dcsdcwdcwdc@mail.com"},
                                       ])
def test_registration_rejects_validation(client,payload):
    response = client.post("/auth/register",json=payload)
    assert response.status_code == 422

def test_successfull_registration(client):
    response = client.post("/auth/register", json={"email":"qwerty123@mail.com",
                                                   "password":"Qwerty123"})
    body = response.json()
    assert response.status_code == 201
    assert body["email"] == "qwerty123@mail.com"
    assert body["id"] > 0

def test_registration_rejects_duplicate_email(client):
    response1 = client.post("/auth/register",json={"email":"qwerty123@mail.com",
                                                   "password":"Qwerty123"})

    response2 = client.post("/auth/register",json={"email":"qwerty123@mail.com",
                                                   "password":"Qwertywecw"})
    assert response1.status_code == 201
    assert response2.status_code == 409
    assert response2.json() == {
        "detail": "Email already registered"
    }


