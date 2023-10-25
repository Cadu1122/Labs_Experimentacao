
from datetime import datetime
from typing import TypedDict

class TokenInfo(TypedDict):
    token: str
    last_use: datetime
    qtd_of_requests_made: int