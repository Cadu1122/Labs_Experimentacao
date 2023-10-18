from datetime import date, datetime
from typing import TypedDict


class Repository(TypedDict):
    name: str
    created_at: date
    stars: int
    merged_prs: int
    closed_issues: int
    total_of_issues: int
    last_update_date: date
    primary_language: str
    total_of_releases: int
    updated_at: datetime