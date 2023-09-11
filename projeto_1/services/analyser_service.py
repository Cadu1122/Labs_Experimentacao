from datetime import date
from projeto_1.core.constants import MOST_FAMOUS_LANGUAGES, PREFER_GET_PERSISTED_DATA_OVER_FETCH, TOTAL_QUANTITY_OF_REPOSITORIES
from projeto_1.models.analysis import Lab1AnalysisObject, get_lab1_analysis_object_from_repositories
from projeto_1.models.repository import Repository
from projeto_1.repository.github.github_most_famous_repo_repository import GithubMostFamousRepoRepository
from projeto_1.services.graphic_service import GraphicService
from projeto_1.shared.date_utils import diff_in_days
from projeto_1.shared.logger import get_logger

logger = get_logger(__name__)

class AnalyzerService:
    def __init__(
        self,
        github_most_famous_repo_repositoriy: GithubMostFamousRepoRepository,
        graphic_service: GraphicService
    ):
        self.__github_most_famous_repo_repositoriy = github_most_famous_repo_repositoriy
        self.__graphic_service = graphic_service
    
    async def analyse_most_famous_repositories(self):
        await self.__github_most_famous_repo_repositoriy.get_most_famous_repositories(
            prefer_to_use_persited_repositories=False
        )
      
