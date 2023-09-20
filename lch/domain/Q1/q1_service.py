from lch.domain.github.models.query_builders.objects.issues_query_builder import IssueStates, IssuesQueryBuilder
from lch.domain.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from lch.domain.github.models.query_builders.objects.releases_query_builder import ReleaseOrderByDirection, ReleaseOrderByField, ReleasesQueryBuilder
from lch.domain.github.models.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.domain.github.models.query_builders.objects.stargazers_query_builder import StargazersQueryBuilder
from lch.domain.github.repository.github_repository import GithubRepository


class Q1Service:
    def __init__(self, github_repository: GithubRepository):
        self.__github_repository = github_repository
    
    async def execute(self):
        repository_query = self.__mount_query()
        search = 'stars:>100'
        self.__github_repository()
    
    def __mount_query(self) -> RepositoryQueryBuilder:
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