from projeto_1.repository.github.query_builders.query_builder import BaseQuery


class StargazersQueryBuilder(BaseQuery):
    def __init__(
        self, 
        has_total_count: bool = False
    ):
        super().__init__(has_total_count=has_total_count)
    
    def build_query(self) -> str:
        total_count = 'totalCount' if self._has_total_count else  ''
        return f'''
            stargazers {{
                {total_count}
            }}
        '''