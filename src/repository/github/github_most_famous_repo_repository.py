import base64
from datetime import date, datetime
from pathlib import Path
from typing import Callable
from lch.models.repository import Repository
from lch.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
from lch.repository.data_persistance.models.serialize_rules import SerializeRule
from lch.repository.github.query_builders.functions.search_query_builder import SearchQueryBuilder, SearchTypes
from lch.repository.github.query_builders.objects.issues_query_builder import IssueStates, IssuesQueryBuilder
from lch.repository.github.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from lch.repository.github.query_builders.objects.releases_query_builder import ReleaseOrderByDirection, ReleaseOrderByField, ReleasesQueryBuilder
from lch.repository.github.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.repository.github.query_builders.objects.stargazers_query_builder import StargazersQueryBuilder
from lch.shared.async_utils import create_async_task, get_async_results
from lch.shared.date_utils import datetime_str_to_date, str_to_datetime
from lch.shared.dict_utils import safe_get_value
from lch.shared.graphql_client import GraphqlClient
from lch.core.constants import BASE_GRAPTHQL_PATH, DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH, TOTAL_QUANTITY_OF_REPOSITORIES
from lch.shared.logger import get_logger
from lch.services.token_service import get_token


logger = get_logger(__name__)

class GithubMostFamousRepoRepository:

    def __init__(
          self,
          data_persistance_repository: DataPersistanceRepository,
          graphql_client: GraphqlClient
    ):
        self.__data_persistance_repository = data_persistance_repository
        self.__graphql_client = graphql_client
    
    def __create_cursor(self, next_page_number: int):
        '''
          Create a cursor to paginate to the next request page
        '''
        cursor = f'cursor:{next_page_number}'.encode()
        return base64.encodebytes(cursor).decode().replace('\n', '')
    
    def __mount_famous_repositories_query(self) -> RepositoryQueryBuilder:
        '''
          Create te query for the most famous repositories\n
          it is composed by:
            - Name of the repository
            - Creation date
            - Total of issues
            - Total of CLOSED issues
            - Total of merged Pull Requests
            - Total of releases
            - Date of the latest update
            - Primary language
            - Total of stars
        '''
        repository = RepositoryQueryBuilder(
            has_created_at=True,
            has_name=True,
            has_primary_language=True,
            has_updated_at=True,
            has_url=True
        )
        repository.compose_with_query(
          IssuesQueryBuilder(
            has_total_count=True,
            state=IssueStates.CLOSED
          ),
          custom_attr='total_of_closed_issues'
        )
        repository.compose_with_query(
          IssuesQueryBuilder(
            has_total_count=True,
          ),
          custom_attr='total_of_issues'
        )
        repository.compose_with_query(
          PullRequestsQueryBuilder(
            has_total_count=True,
            state=PullRequestsState.MERGED
          )
        )
        repository.compose_with_query(
          ReleasesQueryBuilder(
            has_total_count=True,
            order_by_field=ReleaseOrderByField.CREATED_AT,
            oder_by_direction=ReleaseOrderByDirection.DESC
          )
        )
        repository.compose_with_query(
            StargazersQueryBuilder(
              has_total_count=True
            ),
            custom_attr='total_of_stars'
        )
        return repository

    def __get_all__possible_search_queries(
        self, 
        base_search_query: SearchQueryBuilder, 
        data_quantity: int
    ):
        '''
          Mounts every query that can be done based on the repository quantity\n
          ---
          Params:
            base_search_query: The base search query to be made
            data_quantity: The total of data that need to be obtained based on the search query
          ---
          Return:
            A list of all queries that need to be done to obtain the specified quantity of repositories 
          ---
            Disclaimer:
              Based on the quantity of repositories the function create a cursor to iterate -> 50 <-
              for query, so if you want to get 100 repositories this function will return two queries.
              
              The quantity of repositories that can be obtained by query can be modified changing
              the value of the DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH constant
        '''
        queries = [base_search_query.build_query()]
        quantity_of_queries = data_quantity // DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH
        for i in range(quantity_of_queries - 1):
            i += 1
            cursor = self.__create_cursor(
                next_page_number=i*DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH
            )
            queries.append(base_search_query.build_query(cursor))
        return queries

    def __persit_most_famous_search_response(self, values: list[Repository]):
        '''
          Persist on a CSV the response of the search request
        '''
        columns = (
            SerializeRule(column_name='name', dict_deserialize_rule=('name',)),
            SerializeRule(column_name='created_at', dict_deserialize_rule=('created_at',)),
            SerializeRule(column_name='merged_prs', dict_deserialize_rule=('merged_prs',)),
            SerializeRule(column_name='total_of_stars', dict_deserialize_rule=('stars',)),
            SerializeRule(column_name='total_of_closed_issues', dict_deserialize_rule=('closed_issues',)),
            SerializeRule(column_name='total_of_issues', dict_deserialize_rule=('total_of_issues',)),
            SerializeRule(column_name='last_update_date', dict_deserialize_rule=('last_update_date',)),
            SerializeRule(column_name='primary_language', dict_deserialize_rule=('primary_language',)),
            SerializeRule(column_name='total_of_releases', dict_deserialize_rule=('total_of_releases',)),
        )
        self.__data_persistance_repository.persist_data_in_csv(
            file_path=Path('resources/repositories.csv'),
            columns=columns,
            data=values
        )

    def __repository_from_csv_row(self, row: tuple[any]):
        return Repository(
            name=row[0],
            created_at=date.fromisoformat(row[1]),
            merged_prs=int(row[2]),
            stars=int(row[3]),
            closed_issues=int(row[4]),
            total_of_issues=int(row[5]),
            last_update_date=datetime.fromisoformat(row[6]),
            primary_language=row[7],
            total_of_releases=int(row[8])
        )

    def __get_famous_repositories_from_csv(self):
      repositories: list[Repository] = []
      persitance_file_path = Path('resources/repositories.csv')
      self.__data_persistance_repository.get_persited_data_in_csv(
              file_path=persitance_file_path,
              mapper_function=lambda row, _: repositories.append(self.__repository_from_csv_row(row))
      )
      return repositories
    
    def __get_most_famous_repositories_reponse_handler(self, response: list[dict[str, any]]):
        repositories: list[Repository] = []
        get_total_count_from_attr = lambda value, attr: value.get(attr).get('totalCount')
        data = safe_get_value(response, ('data',), default_value={})
        for value in data.get('search', {}).get('nodes', []):
            primary_language =  safe_get_value(value, ('primaryLanguage', 'name'))
            repositories.append(Repository(
                name=value.get('name'),
                created_at=datetime_str_to_date(value.get('createdAt')),
                primary_language=primary_language,
                closed_issues=get_total_count_from_attr(value, 'total_of_closed_issues'),
                total_of_issues=get_total_count_from_attr(value, 'total_of_issues'),
                merged_prs=get_total_count_from_attr(value, 'pullRequests'),
                total_of_releases=get_total_count_from_attr(value, 'releases'),
                last_update_date=str_to_datetime(value.get('updatedAt')),
                stars=get_total_count_from_attr(value, 'total_of_stars')
            ))
        return repositories

    async def __execute_queries(self, queries: list[str], response_handler: Callable[[any], any]):
        tasks = []
        for query in queries:
            tasks.append(
                create_async_task(
                  self.__graphql_client.execute_query,
                  path=BASE_GRAPTHQL_PATH,
                  query=query,
                  auth_token=get_token()
                )
            )
        logger.debug('Executing queries...')
        responses = await get_async_results(tasks)
        logger.debug('Queries executed!')

        logger.debug('Mapping values')
        result = []
        for response in responses:
            response = response_handler(response)
            result.extend(response)
        logger.debug(f'{len(result)} values mapped!')

        return result

    async def get_most_famous_repositories(
        self, 
        qtd_of_repositories = TOTAL_QUANTITY_OF_REPOSITORIES,
        prefer_to_use_persited_repositories: bool = True
    ):
        '''
          ---
          Get the most famous repositories based on the quantity of stars
          ---
          Params:
            qtd_of_repositories: The quantity of repositories, default as 1_000
          ---
          Returns:
            A list of dicts of the most famous repositories
        '''
        repositories: list[Repository] = []
        
        if prefer_to_use_persited_repositories:
            if repositories := self.__get_famous_repositories_from_csv():
                return repositories

        logger.debug(f'Preparing to obtain the {qtd_of_repositories} famous repositories')
        search_query = SearchQueryBuilder(
            first=DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH,
            search_type=SearchTypes.REPOSITORY,
            search_query="stars:>100",
            has_page_info=True
        )
        search_query.with_repository(self.__mount_famous_repositories_query())
        logger.debug('Building queries...')
        queries = self.__get_all__possible_search_queries(
            base_search_query=search_query,
            data_quantity=qtd_of_repositories
        )
        logger.debug(f'{len(queries)} queries mounted!')

        repositories: list[Repository] = await self.__execute_queries(queries, self.__get_most_famous_repositories_reponse_handler)
        logger.debug(f'Queries executed! {len(repositories)} responses obtained')

        logger.debug('Persisting responses...')
        self.__persit_most_famous_search_response(repositories)
        logger.debug('Responses persisted!')

        return repositories
