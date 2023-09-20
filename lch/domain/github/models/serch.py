from dataclasses import dataclass
from typing import Optional


@dataclass
class Search:
    stars: Optional[int]
    language: Optional[str]