from typing import Optional
from enum import Enum
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder

from lch.modules.github.models.query_builders.query_builder import QueryBuilder

class SearchTypes(Enum):
    REPOSITORY = 'REPOSITORY'

class RepositoryFunctionQueryBuilder():
    def __init__(
        self,
        owner: str,
        name: str
    ):
        self.__owner = owner
        self.__name = name
        self.__nodes: list[QueryBuilder] = []

    def with_pr(self, pr: PullRequestsQueryBuilder):
        self.__nodes.append(pr)
    
    def __format_nodes(self, cursor: str = None):
        formatted_nodes = ''
        base_query = ''
        for node in self.__nodes:
            # TODO: Not all QueryBuilders have cursors..., create a new generic paginated builder
            formatted_node = node.build_query(cursor=cursor)
            formatted_nodes += f'{base_query}{formatted_node}'
        return formatted_nodes
    
    def __get_function_name(self):
        return f'''
            repository(
                owner: "{self.__owner}",
                name: "{self.__name}"
            )
        '''

    def build_query(self, cursor: str = None) -> str:
        function_name = self.__get_function_name()
        nodes = self.__format_nodes(cursor)
        return f'''
            query {{
                {function_name}{{
                    {nodes}
                }}
            }}
        '''
        