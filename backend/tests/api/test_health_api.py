

def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_local_frontend_origin_is_allowed(client):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:4173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4173"
