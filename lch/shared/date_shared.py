from datetime import date

def datetime_str_to_date(value: str):
    if value:
        value = value.split('T')[0]
        return date.fromisoformat(value)

def diff_in_years(a: date, b: date):
    return (a - b).days // 365