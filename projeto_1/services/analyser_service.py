from core.constants import TOTAL_QUANTITY_OF_REPOSITORIES
from repository.github.github_repository import GithubRepository


class AnalyzerService:
    def __init__(
        self,
        github_repositoriy: GithubRepository
    ):
        self.__github_repository = github_repositoriy
    
    async def analyse_most_famous_repositories(self):
        repositories = self.__github_repository.get_most_famous_repositories(
            qtd_of_repositories=TOTAL_QUANTITY_OF_REPOSITORIES
        )