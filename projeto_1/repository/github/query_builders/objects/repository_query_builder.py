from projeto_1.repository.github.query_builders.custom_composable_query import CustomComposableQuery
from projeto_1.repository.github.query_builders.query_builder import BaseQuery, QueryBuilder


class RepositoryQueryBuilder(BaseQuery):
    def __init__(
        self,
        has_total_count: bool = False,
        has_created_at: bool = False,
        has_name: bool = False
    ):
        super().__init__(has_created_at=has_created_at,has_total_count=has_total_count)
        self.__composable_queries: list[CustomComposableQuery] = []
        self.__has_name = has_name

    def with_name(self):
        self.__has_name = True
    
    def compose_with_query(
        self, 
        query: QueryBuilder,
        custom_attr: str = None
    ):
        self.__composable_queries.append(CustomComposableQuery(
            query=query,
            custom_attr=custom_attr
        ))
    
    def __format_queries(self):
        resutl = ''
        for composable_query in self.__composable_queries:
            formatted_query = composable_query.query.build_query()
            if composable_query.custom_attr:
                formatted_query = f'{composable_query.custom_attr}: {formatted_query}'
            resutl += formatted_query
        return resutl

    def build_query(self) -> str:
        name = 'name' if self.__has_name else ''
        created_at = 'createdAt' if self._has_created_at else '' 
        total_count = 'totalCount' if self._has_total_count else ''
        queries = self.__format_queries()
        return f'''
            Repository {{
                {name}
                {created_at}
                {total_count}
                {queries}
            }}
        '''