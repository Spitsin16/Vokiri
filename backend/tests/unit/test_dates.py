from datetime import datetime, timezone

from backend.utils.dates import moscow_today


def test_moscow_today_uses_moscow_calendar_day():
    late_evening_utc = datetime(2026, 11, 3, 22, 30, tzinfo=timezone.utc)

    assert moscow_today(late_evening_utc).isoformat() == "2026-11-04"
