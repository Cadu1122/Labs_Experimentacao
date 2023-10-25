import base64
from datetime import datetime
import json
from typing import Any, Callable
from lch.core.clients.graphql_client import GraphqlClient
from lch.core.config.constants import BASE_GRAPTHQL_PATH, DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH, GITHUB_AUTH_TOKEN_V2_PATH, MAX_REQUESTS_PER_HOUR_IN_GITHUB
from lch.core.logger import get_logger
from lch.modules.github.github_service import GithubService
from lch.modules.github.models.query_builders.functions.repository_function_query_builder import RepositoryFunctionQueryBuilder
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder
from lch.modules.github.models.query_builders.query_builder import QueryBuilder
from lch.modules.github.models.token import TokenInfo
from lch.shared.async_shared import create_async_task, run_tasks
from lch.shared.date_shared import diff_in_hours, str_to_datetime
from lch.shared.process_shared import BackgroundMessagersProcessPool

logger = get_logger(__name__)

class GithubServiceV2:
    def __init__(
        self, 
        github_service_v1: GithubService,
        graphql_client: GraphqlClient
    ):
        self.__graphql_client = graphql_client
        self.__github_service_v1 = github_service_v1
    
    async def search(
        self, 
        search: str,
        query: QueryBuilder,
        quantity_of_itens: int,
        custom_mapper: Callable[[dict], Any] = lambda value: value
    ):
        return await self.__github_service_v1.search(search, query, quantity_of_itens, custom_mapper)

    async def execute_queries(
        self, 
        token: str,
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
                    auth_token=token
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


    # TODO: quantity_of_prs should be optional 
    async def get_prs_from_repository(
        self,
        owner: str,
        name: str,
        pr_query: PullRequestsQueryBuilder,
        quantity_of_prs: int
    ):
        repository_query = RepositoryFunctionQueryBuilder(owner=owner, name=name)
        repository_query.with_pr(pr_query)

        queries = self.__mount_all_possible_queries(
            query=repository_query,
            quantity_of_itens=quantity_of_prs,
            itens_per_page=pr_query.quantity_of_itens_per_query
        )
        print(len(queries))
        # total_of_queries = len(queries)
        # tokens = self.__get_tokens_to_be_used()
        # queries_per_token: list[tuple[TokenInfo, list[str]]] = []
        # Pegar os repos e colocar em uma fila, essa fila 
        # Particionar as queries
        # Distribuir os tokens
        # Monitorar as queries que sobram

    def __create_cursor(self, page: int):
        cursor = f'cursor:{page}'.encode()
        return base64.encodebytes(cursor).decode().replace('\n', '')
    
    def mount_all_possible_queries(
        self, 
        query: QueryBuilder, 
        quantity_of_itens: int, 
        itens_per_page: int = DEFAULT_QUANTITY_OF_ITEMS_TO_FETCH,
        ignore_first: int = False
    ):
        logger.debug('Mounting all possible queries')
        queries: list[str] = []
        quantity_of_queries = quantity_of_itens / itens_per_page
        if quantity_of_queries % 2 != 0:
            # PLUS TWO CAUSE I START FROM 0...
            quantity_of_queries = int(quantity_of_queries) + 1
        logger.debug('Mouting every possible paginated query')
        for i in range(int(quantity_of_queries)):
            i = i + 1 if ignore_first else i
            cursor = self.__create_cursor(
                page=i*itens_per_page
            )
            queries.append(query.build_query(cursor))
        logger.debug(f'All queries mounted! {len(queries)}')
        return queries

    def __get_tokens_to_be_used(self):
        logger.debug('Getting disponible tokens to execute requests')
        tokens: dict[str, TokenInfo] = {}
        disponible_tokens: dict[str, TokenInfo] = {}
        with open(GITHUB_AUTH_TOKEN_V2_PATH) as f:
            tokens = json.load(f)
        for key, token_info in tokens.items():
            token_info['last_use'] = str_to_datetime(token_info.get('last_use'))
            if self.__is_token_avaible_for_use(token_info):
                disponible_tokens[key] = token_info
        logger.debug(f'All disponible tokens gotten {disponible_tokens}')
        return disponible_tokens
    
    def __is_token_avaible_for_use(self, token_info: TokenInfo):
        there_requests_available = token_info.get('qtd_of_requests_made') < MAX_REQUESTS_PER_HOUR_IN_GITHUB
        if not there_requests_available:
            now = datetime.now()
            already_available_for_reuse = diff_in_hours(now, token_info.get('last_use')) > 1
            return already_available_for_reuse
        return True

    def __partition_queries_per_token(self, tokens: dict[str, TokenInfo], queries: list[str]):
        total_of_queries = len(queries)
        partioned_queries: tuple(list[tuple[dict[str, TokenInfo], list[str]]], list[str]) = []
        last_gotten_idx
        for key, token_info in tokens:
            ...