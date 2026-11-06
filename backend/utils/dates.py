from datetime import date, datetime
from zoneinfo import ZoneInfo


MOSCOW_TIMEZONE = ZoneInfo("Europe/Moscow")


def moscow_today(now: datetime | None = None) -> date:
    current_time = now or datetime.now(MOSCOW_TIMEZONE)
    return current_time.astimezone(MOSCOW_TIMEZONE).date()
