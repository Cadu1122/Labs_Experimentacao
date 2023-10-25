from pathlib import Path
from lch.core.logger import get_logger
from lch.modules.github.github_service import GithubService
from lch.modules.github.github_service_v2 import GithubServiceV2
from lch.modules.github.models.query_builders.functions.repository_function_query_builder import RepositoryFunctionQueryBuilder
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder
from lch.modules.github.models.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.modules.persistance.csv_service import CsvService
from lch.modules.questions.question_3.models.repository import Repository, from_csv, from_github_response
from lch.shared.process_shared import BackgroundMessagersProcessPool

logger = get_logger(__name__)

class Q3Service:
    def __init__(
        self, 
        github_service: GithubService, 
        csv_service: CsvService,
        github_service_v2: GithubServiceV2
    ):
        self.__github_service_v2 = github_service_v2
        self.__github_service = github_service
        self.__csv_service = csv_service

        self.__base_resource_path = 'resources/RQ3'
        self.__base_data_resource_path = f'{self.__base_resource_path}/data'
        self.__repositories_path = f'{self.__base_data_resource_path}/repositories.csv'

    
    async def get_famous_repositories(self, prefer_persisted_repos = True):
        logger.debug('Getting most famous repositories')
        repositories: list[Repository] = []
        if prefer_persisted_repos:
            repositories = self.__get_persited_repositories()
        if not repositories:
            logger.debug('No persisted repositories found, fetching from api...')
            query = RepositoryQueryBuilder(has_name_with_owner=True)
            query.compose_with_query(PullRequestsQueryBuilder(has_total_count=True))
            repositories = await self.__github_service.search(
                search='stars:>100',
                query=query,
                quantity_of_itens=200,
                custom_mapper=from_github_response
            )
            logger.debug('Most famous repositories gotten')
            self.__persit_repositories(repositories)
        return repositories
    
    async def execute_queries(self, token: str, queries: list[str]):
        return await self.__github_service_v2.execute_queries(
            token=token,
            queries=queries
        )

    def __persit_repositories(self, repositories: list[Repository]):
        logger.debug(f'Persisting {len(repositories)} repositories')
        self.__csv_service.persist_shallow_dict_in_csv(
            save_path=self.__repositories_path, 
            data=repositories
        )
        logger.debug('All repositories persisted')
    
    def __get_persited_repositories(self):
        logger.debug('Getting persited repositories')
        repositories = self.__csv_service.get_persited_data_in_csv(
            file_path=Path(self.__repositories_path),
            mapper_function=from_csv
        )
        logger.debug(f'Gotten {len(repositories)} repositories persisted')
        return repositories 

    def get_all_possible_queries_per_repo(self, repository: Repository):
        pr_query = PullRequestsQueryBuilder(
            has_additions_count=True,
            has_body=True,
            has_closed_at=True,
            has_comment_count=True,
            has_deletion_count=True,
            has_merged_at=True,
            has_participants_count=True,
            quantity_of_itens_per_query=50
        )
        repository_query = RepositoryFunctionQueryBuilder(
            owner=repository.get('owner'), 
            name=repository.get('name')
        )
        repository_query.with_pr(pr_query)

        return self.__github_service_v2.mount_all_possible_queries(
            query=repository_query,
            quantity_of_itens=repository.get('total_of_prs'),
            itens_per_page=pr_query.quantity_of_itens_per_query
        )