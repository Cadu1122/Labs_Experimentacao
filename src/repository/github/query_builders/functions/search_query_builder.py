from typing import Optional
from src.repository.github.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from enum import Enum

class SearchTypes(Enum):
    REPOSITORY = 'REPOSITORY'

class SearchQueryBuilder():
    def __init__(
        self,
        first: int,
        search_type: SearchTypes,
        search_query: str,
        has_page_info: bool = False
    ):
        self.__nodes = []
        self.__first = first
        self.__type =  search_type
        self.search_query = search_query
        self.__has_page_info = has_page_info
        self.__formatted_nodes: Optional[str] = None
        self.__formatted_page_info: Optional[str] = None

    def with_repository(self, repository: RepositoryQueryBuilder):
        self.__nodes.append(repository)
    
    def with_page_info(self):
        self.__has_page_info = True
    
    def __format_nodes(self):
        if self.__formatted_nodes:
            return self.__formatted_nodes
        self.__formatted_nodes = ''
        base_query = '... on '
        for node in self.__nodes:
            formatted_node = node.build_query()
            self.__formatted_nodes += f'{base_query}{formatted_node}'
        return self.__formatted_nodes
    
    def __get_function_name(self, cursor: str = None):
        cursor = f'after: "{cursor}",' if cursor else ''
        return f'''
            search(
                {cursor}
                first: {self.__first},
                type: {self.__type.value},
                query: "{self.search_query}"
            )
        '''
    
    def __get_page_info(self):
        if self.__formatted_page_info:
            return self.__formatted_page_info
        self.__formatted_page_info = '''
            pageInfo{
                endCursor
                hasNextPage
            }
        ''' if self.__has_page_info else ''
        return self.__formatted_page_info

    def build_query(self, cursor: str = None) -> str:
        function_name = self.__get_function_name(cursor)
        page_info = self.__get_page_info()
        nodes = self.__format_nodes()
        return f'''
            query {{ {function_name}{{
                    {page_info}
                    nodes {{
                        {nodes}
                    }}
                }}
            }}
        '''
        