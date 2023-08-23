from enum import Enum
from repository.github.query_builders.query_builder import BaseQuery

class ReleaseOrderByField(Enum):
    CREATED_AT = 'CREATED_AT'

class ReleaseOrderByDirection(Enum):
    DESC = 'DESC'

class ReleasesQueryBuilder(BaseQuery):
    def __init__(
        self,
        first: int = None,
        has_total_count: bool = False,
        order_by_field: ReleaseOrderByField = None,
        oder_by_direction: ReleaseOrderByDirection = None
    ):
        super().__init__(has_total_count=has_total_count)
        self.__first = first
        self.__order_by_field = order_by_field
        self.__order_by_direction = oder_by_direction
    
    def with_order_by(self, field: ReleaseOrderByField, direction: ReleaseOrderByDirection):
        self.__order_by_field = field
        self.__order_by_direction = direction
    
    def with_first(self, first: int):
        self.__first = first

    def __mount_order_by(self):
        if self.__order_by_direction and self.__order_by_field:
            return f'''
                orderBy: {{ field: {self.__order_by_field.value}, direction: {self.__order_by_direction.value} }}
            '''
        return ''
    
    def build_query(self) -> str:
        field_name = 'releases'

        total_count = 'totalCount' if self._has_total_count else ''
        first = f'first: {first}' if self.__first else  ''
        order_by = self.__mount_order_by()

        if order_by or first:
            fields = ','.join([first, order_by]) 
            field_name = f'{field_name}({fields})'
        return f'''
            {field_name}{{ 
                {total_count} 
            }}
        '''
        
