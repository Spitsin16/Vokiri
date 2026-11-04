from datetime import date

import pytest

from backend.utils.activity_streak import get_streak_list


@pytest.mark.parametrize(
    ("activity_dates", "expected_streaks"),
    [
        ([], []),
        ([date(2026, 11, 1)], [1]),
        (
            [
                date(2026, 11, 1),
                date(2026, 11, 2),
                date(2026, 11, 3),
            ],
            [3],
        ),
        (
            [
                date(2026, 11, 1),
                date(2026, 11, 2),
                date(2026, 11, 4),
            ],
            [2, 1],
        ),
        (
            [
                date(2026, 11, 1),
                date(2026, 11, 3),
                date(2026, 11, 4),
            ],
            [1, 2],
        ),
    ],
)
def test_get_streak_list(activity_dates, expected_streaks):
    assert get_streak_list(activity_dates) == expected_streaks
