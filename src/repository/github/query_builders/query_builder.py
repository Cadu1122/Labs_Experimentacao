from typing import Protocol

class QueryBuilder(Protocol):
    def build_query(self) -> str:
        raise NotImplementedError

class BaseQuery(QueryBuilder):
    def __init__(
        self,
        has_total_count: bool = False,
        has_created_at: bool = False
    ):
        self._has_total_count = has_total_count
        self._has_created_at = has_created_at
    
    def with_total_count(self):
        self._has_total_count = True
    
    def with_created_at(self):
        self._has_created_at = True
