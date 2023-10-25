import base64
from pathlib import Path
from typing import Any, Callable
from lch.core.config.constants import BASE_GRAPTHQL_PATH, DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH, GITHUB_AUTH_TOKEN_PATH
from lch.core.clients.graphql_client import GraphqlClient
from lch.core.logger import get_logger
from lch.modules.github.models.query_builders.functions.search_query_builder import SearchQueryBuilder, SearchTypes
from lch.modules.github.models.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.modules.github.models.query_builders.query_builder import QueryBuilder
from lch.modules.persistance.file_service import FileService
from lch.shared.async_shared import create_async_task, run_tasks
from git import Repo

logger = get_logger(__name__)

class GithubService:
    def __init__(
        self, 
        graphql_client: GraphqlClient, 
        file_service: FileService
    ):
        self.__graphql_client = graphql_client
        self.__file_service = file_service
        self.__auth_token: str = None
    
    async def search(
        self, 
        search: str,
        query: QueryBuilder,
        quantity_of_itens: int,
        custom_mapper: Callable[[dict], Any] = lambda value: value
    ):
        logger.debug(f'Preparing to execute query -> {search}')
        self.__validate_query_builder_for_search(query)
        search_query_builder = SearchQueryBuilder(
            first=DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH,
            search_type=SearchTypes.REPOSITORY,
            search_query=search,
            has_page_info=True
        )
        search_query_builder.with_repository(query)
        queries = self.mount_all_possible_queries(search_query_builder, quantity_of_itens)
        return await self.__execute_queries(queries, custom_mapper)

    def clone(self, url: str, save_path: Path):
        Repo.clone_from(
            url, 
            save_path, 
            multi_options=(
                '--quiet',
                '--depth=1',
                '--no-tags',
                '--single-branch'
            )
        )
        return save_path
    
    def __validate_query_builder_for_search(self, query: QueryBuilder):
        logger.debug('Validating query to execute search')
        if not isinstance(query, RepositoryQueryBuilder):
            raise ValueError(f'Query of type {type(query)} is not supported')
    
    def mount_all_possible_queries(self, query: QueryBuilder, quantity_of_itens: int):
        queries: list[str] = []
        quantity_of_queries = quantity_of_itens // DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH
        logger.debug('Mouting every possible paginated query')
        for i in range(quantity_of_queries):
            cursor = self.__create_cursor(
                page=i*DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH
            )
            queries.append(query.build_query(cursor))
        logger.debug(f'{len(queries)} queries mounted')
        return queries

    def __create_cursor(self, page: int):
        cursor = f'cursor:{page}'.encode()
        return base64.encodebytes(cursor).decode().replace('\n', '')

    def __get_auth_token(self):
        if not self.__auth_token:
            token = self.__file_service.get_data_from_file(file_path=Path(GITHUB_AUTH_TOKEN_PATH))[0]
            self.__auth_token = token
        return self.__auth_token

    async def __execute_queries(
        self, 
        queries: list[str],
        response_handler: Callable[[dict], Any] = lambda value: value
    ):
        logger.debug(f'Will make {len(queries)} requests')
        result = []
        tasks = []
        for query in queries:
            tasks.append(
                create_async_task(
                    self.__graphql_client.execute_query,
                    path=BASE_GRAPTHQL_PATH,
                    query=query,
                    auth_token=self.__get_auth_token()
                )
            )
        responses = await run_tasks(tasks)
        for response in responses:
            response = response_handler(response)
            if type(response) is list:
                result.extend(response)
            else:
                result.append(response)
        logger.debug(f'{len(responses)} responses gotten')
        return result