from src.repository.github.query_builders.query_builder import BaseQuery
from enum import Enum

class PullRequestsState(Enum):
    MERGED = 'MERGED'

class PullRequestsQueryBuilder(BaseQuery):
    def __init__(
        self,
        has_total_count: bool = False,
        state: PullRequestsState = None
    ):
        super().__init__(has_total_count=has_total_count)
        self.__state = state
    
    def build_query(self) -> str:
        field_name = 'pullRequests'
        if self.__state:
            field_name += f'(states: {self.__state.value})'
        total_count = 'totalCount' if self._has_total_count else ''
        return f'''
            {field_name}{{ 
                {total_count} 
            }}
        '''