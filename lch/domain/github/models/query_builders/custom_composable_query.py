from dataclasses import dataclass
from typing import Optional

from lch.domain.github.models.query_builders.query_builder import QueryBuilder


@dataclass
class CustomComposableQuery:
    query: QueryBuilder
    custom_attr: Optional[str] = None