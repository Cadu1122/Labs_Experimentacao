from typing import Optional, TypedDict

class Repository(TypedDict):
    name: str
    url: str
    stars: int
    releases: int
    age: int
    composed_repo_name: Optional[str]