from dataclasses import dataclass
from typing import Optional

from projeto_1.repository.github.query_builders.query_builder import QueryBuilder


@dataclass
class CustomComposableQuery:
    query: QueryBuilder
    custom_attr: Optional[str] = None