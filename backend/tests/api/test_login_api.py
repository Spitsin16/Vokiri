import pytest

def test_success_login(client):
    client.post("/auth/register", json = {"email":"testemail@mail.com",
                                                      "password":"TestPassword"})

    response = client.post("/auth/login", json = {"email":"testemail@mail.com",
                                                      "password":"TestPassword"})

    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer"

@pytest.mark.parametrize(("email","password"), [("testemail@mail.com","Password"),("sscsc@mail.com","Passqwx8")])
def test_wrong_email(client,email,password):
    client.post("/auth/register", json = {"email":"testemail@mail.com",
                                                      "password":"TestPassword"})
    response = client.post("/auth/login",json = {"email": email,
                                                 "password": password})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Wrong email or password"
    }