import pytest


@pytest.mark.parametrize("limit", [0, 51])
def test_today_cards_rejects_limit_outside_allowed_range(
    client,
    authenticated_user,
    limit,
):
    response = client.get(
        "/review/today",
        params={"limit": limit},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 422


def test_today_cards_accepts_limit_inside_allowed_range(
    client,
    authenticated_user,
):
    response = client.get(
        "/review/today",
        params={"limit": 20},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    assert response.json() == []
