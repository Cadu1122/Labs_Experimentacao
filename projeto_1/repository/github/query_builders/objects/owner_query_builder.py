from projeto_1.repository.github.query_builders.query_builder import QueryBuilder

class OwnerQueryBuilder(QueryBuilder):
    def __init__(
        self,
        has_login,
    ):
        self.__has_login = has_login

    def with_login(self, value: int):
        self.__has_login = value

    def build_query(self) -> str:
        field_name = 'owner'
        login = 'login' if self.__has_login else ''
        return f'''
            {field_name} {{
                {login}
            }}
        '''