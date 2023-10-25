from copy import deepcopy
from lch.modules.github.models.query_builders.query_builder import BaseQuery
from enum import StrEnum

class PullRequestsState(StrEnum):
    MERGED = 'MERGED'
    CLOSED = 'CLOSED'

class PullRequestsQueryBuilder(BaseQuery):
    def __init__(
        self,
        has_total_count: bool = False,
        has_closed_at: bool = False,
        has_deletion_count: bool = False,
        has_merged_at: bool = False,
        has_additions_count: bool = False,
        has_participants_count: bool = False,
        has_body: bool = False,
        has_comment_count: bool = False,
        has_created_at: bool = False,
        state: list[PullRequestsState] = None,
        quantity_of_itens_per_query: int = None,
    ):
        super().__init__(has_total_count=has_total_count, has_created_at=has_created_at)
        self.__states = deepcopy(state)
        self.quantity_of_itens_per_query = quantity_of_itens_per_query
        self.__has_closed_at = has_closed_at
        self.__has_deletion_count = has_deletion_count
        self.__has_merged_at = has_merged_at
        self.__has_additions_count = has_additions_count
        self.__has_body = has_body
        self.__has_comment_count = has_comment_count
        self.__has_participants_count = has_participants_count
    
    def __get_function_name(self, cursor: str = None):
        function_name = 'pullRequests'
        if self.__states:
            states = ','.join(self.__states)
            function_name += f'(states: [{states}]'
        if self.quantity_of_itens_per_query:
            first = f'first: {self.quantity_of_itens_per_query}'
            if '(' in function_name:
                function_name += ','
            function_name += f'{first}'
        if cursor:
            function_name += f', after: "{cursor}"'
        if '(' in function_name:
            function_name += ')'
        return function_name
    
    def __get_node_expression(self):
        created_at = 'createdAt'
        merged_at = 'mergedAt' if self.__has_merged_at else  ''
        closed_at = 'closedAt' if self.__has_closed_at else ''
        deletion_count = 'deletions' if self.__has_deletion_count else ''
        additions_count = 'additions' if self.__has_additions_count else  ''
        body = 'body' if self.__has_body else  ''
        comment_count = 'comments(first: 1) { totalCount }' if self.__has_comment_count else ''
        participants_count = 'participants(first: 1) { totalCount }' if self.__has_participants_count else ''
        if created_at or merged_at or closed_at or deletion_count or additions_count or body or comment_count or participants_count:
            return  f'''
                nodes {{
                    {created_at}
                    {merged_at}
                    {closed_at}
                    {deletion_count}
                    {additions_count}
                    {body}
                    {comment_count}
                    {participants_count}
                }}
            '''
        return ''
    
    def build_query(self, cursor: str = None) -> str:
        self.__states = [PullRequestsState.MERGED, PullRequestsState.CLOSED]
        function_name = self.__get_function_name(cursor)
        total_count = 'totalCount' if self._has_total_count else ''
        node = self.__get_node_expression()
        return f'''
            {function_name}{{ 
                {total_count} 
                {node}
            }}
        '''