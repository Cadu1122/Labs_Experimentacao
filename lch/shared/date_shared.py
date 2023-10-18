from datetime import UTC, date, datetime

def datetime_str_to_date(value: str):
    if value:
        value = value.split('T')[0]
        return date.fromisoformat(value)

def diff_in_years(a: date, b: date):
    return (a - b).days // 365

def datetime_str_to_date(value: str):
    if value:
        value = value.split('T')[0]
        return date.fromisoformat(value)

def str_to_datetime(value: str):
    if value:
        return datetime.fromisoformat(value)

def diff_in_days(a: date, b: date):
    return (a - b).days

def diff_in_years(a: date, b: date):
    return (a - b).days // 365

def diff_in_hours(a: datetime, b: datetime):
    a = a.replace(tzinfo=UTC)
    b = b.replace(tzinfo=UTC)
    return (a - b).total_seconds() / 3600