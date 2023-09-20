from enum import Enum

from lch.domain.github.models.query_builders.query_builder import QueryBuilder

class IssueStates(Enum):
    CLOSED = 'CLOSED'

class IssuesQueryBuilder(QueryBuilder):
    def __init__(
        self,
        has_total_count: bool = False,
        state: IssueStates = None,
        first: int = None
    ):
        self._has_total_count = has_total_count
        self.__state = state
        self.__first = first

    def with_total_count(self):
        self._has_total_count = True
    
    def with_state(self, state: IssueStates):
        self.__state = state
    
    def with_first(self, value: int):
        self.__first = value

    def __should_mount_as_function(self):
        return self.__state != None or self.__first != None

    def build_query(self) -> str:
        field_name = 'issues'
        if self.__should_mount_as_function():
            first = f'first: {self.__first}' if self.__first else ''
            state = f'states: {self.__state.value}' if self.__state else  ''
            function_attrs = ','.join([first, state])
            field_name = f'{field_name}({function_attrs})'
        total_count = 'totalCount' if self._has_total_count else ''
        return f'''
            {field_name} {{
                {total_count}
            }}
        '''