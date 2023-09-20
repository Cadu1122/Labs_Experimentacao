from lch.repository.github.query_builders.query_builder import QueryBuilder


class LanguagesQueryBuilder(QueryBuilder):
    def __init__(
        self,
        has_name: bool = False,
        first: int = None
    ):
        self.__first = first
        self.__has_name = has_name

    def with_first(self, value: int):
        self.__first = value
    
    def with_name(self):
        self.__has_name = True
    
    def build_query(self) -> str:
        field_name = 'languages'
        name = 'name' if self.__has_name else  ''
        first = f'first: {self.__first}' if self.__first else  ''
        if first:
            field_name = f'{field_name}({first})'
        return f'''
            {field_name}{{
                nodes {{
                    {name}
                }}
            }}
        '''