from datetime import datetime, timezone


def dt_now() -> datetime:
    return datetime.now(timezone.utc)
