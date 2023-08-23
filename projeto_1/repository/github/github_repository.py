import base64
from pathlib import Path
from projeto_1.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
from projeto_1.repository.data_persistance.models.serialize_rules import SerializeRule
from projeto_1.repository.github.query_builders.functions.search_query_builder import SearchQueryBuilder, SearchTypes
from projeto_1.repository.github.query_builders.objects.issues_query_builder import IssueStates, IssuesQueryBuilder
from projeto_1.repository.github.query_builders.objects.latest_release_query_builder import LatestReleaseQueryBuilder
from projeto_1.repository.github.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from projeto_1.repository.github.query_builders.objects.releases_query_builder import ReleaseOrderByDirection, ReleaseOrderByField, ReleasesQueryBuilder
from projeto_1.repository.github.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from projeto_1.repository.github.query_builders.objects.stargazers_query_builder import StargazersQueryBuilder
from projeto_1.shared.async_utils import create_async_task, get_async_results
from projeto_1.shared.graphql_client import GraphqlClient
from projeto_1.core.constants import BASE_GRAPTHQL_PATH, DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH, GITHUB_AUTH_TOKEN
from projeto_1.shared.logger import get_logger


logger = get_logger(__name__)

class GithubRepository:

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
            - Date of the latest release
            - Primary language
            - Total of stars
        '''
        repository = RepositoryQueryBuilder(
            has_created_at=True,
            has_name=True,
            has_primary_language=True
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
          LatestReleaseQueryBuilder(
            has_total_count=True,
            has_created_at=True
          )
        )
        repository.compose_with_query(
            StargazersQueryBuilder(
              has_total_count=True
            ),
            custom_attr='total_of_starts'
        )
        return repository

    def __get_all__possible_search_queries(
        self, 
        base_search_query: SearchQueryBuilder, 
        repository_quantity: int
    ):
        '''
          Mounts every query that can be done based on the repository quantity\n
          ---
          Params:
            base_search_query: The base search query to be made
            repository_quantity: The total of repositories that need to be obtained based on the search query
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
        quantity_of_queries = repository_quantity // DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH
        for i in range(quantity_of_queries - 1):
            i += 1
            cursor = self.__create_cursor(
                next_page_number=i*DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH
            )
            queries.append(base_search_query.build_query(cursor))
        return queries

    def __persit_search_response(self, values: list[dict]):
        '''
          Persist on a CSV the response of the search request
        '''
        columns = (
            SerializeRule(column_name='name', dict_deserialize_rule=('name',)),
            SerializeRule(column_name='created_at', dict_deserialize_rule=('createdAt',)),
            SerializeRule(column_name='total_of_stars', dict_deserialize_rule=('total_of_starts', 'totalCount')),
            SerializeRule(column_name='total_of_closed_issues', dict_deserialize_rule=('total_of_closed_issues', 'totalCount')),
            SerializeRule(column_name='total_of_issues', dict_deserialize_rule=('total_of_issues', 'totalCount')),
            SerializeRule(column_name='last_release_date', dict_deserialize_rule=('latestRelease', 'createdAt')),
            SerializeRule(column_name='primary_language', dict_deserialize_rule=('primaryLanguage', 'name'))
        )
        nodes = []
        for value in values:
            nodes.extend(value.get('data').get('search').get('nodes'))
        self.__data_persistance_repository.persist_data_in_csv(
            file_path=Path('resources/repositories.csv'),
            columns=columns,
            data=nodes
        )

    async def get_most_famous_repositories(
        self, 
        qtd_of_repositories = 1_000,
        prefer_to_use_persited_repositories: bool = True
    ):
        '''
          ---
          Get the most famous repositories based on the quantity of starts
          ---
          Params:
            qtd_of_repositories: The quantity of repositories, default as 1_000
          ---
          Returns:
            A list of dicts of the most famous repositories
        '''
        # TODO:
        # - Fetch repositories if local file isn't filled
        # - Create model for repository - prefer Typedict over dataclass or something
        persitance_file_path = Path('resources/repositories.csv')
        if prefer_to_use_persited_repositories:
            return self.__data_persistance_repository.get_persited_data_in_csv(
                file_path=persitance_file_path
            )
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
            repository_quantity=qtd_of_repositories
        )
        logger.debug(f'{len(queries)} queries mounted!')
        tasks = []
        for query in queries:
            tasks.append(
                create_async_task(
                  self.__graphql_client.execute_query,
                  BASE_GRAPTHQL_PATH,
                  query,
                  GITHUB_AUTH_TOKEN
                )
            )
        logger.debug('Executing queries...')
        responses = await get_async_results(tasks)
        logger.debug(f'Queries executed! {len(responses)} responses obtained')

        logger.debug('Persisting responses...')
        self.__persit_search_response(responses)
        logger.debug('Responses persisted!')

        return responses
