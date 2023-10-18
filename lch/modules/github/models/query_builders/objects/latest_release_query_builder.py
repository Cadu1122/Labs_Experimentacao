from lch.modules.github.models.query_builders.query_builder import BaseQuery


class LatestReleaseQueryBuilder(BaseQuery):
    def build_query(self):
        created_at = 'createdAt' if self._has_created_at else  ''
        return f'''
            latestRelease {{ 
                {created_at} 
            }}
        '''