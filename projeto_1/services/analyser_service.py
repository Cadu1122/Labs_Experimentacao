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
        repositories = await self.__github_most_famous_repo_repositoriy.get_most_famous_repositories(
            prefer_to_use_persited_repositories=PREFER_GET_PERSISTED_DATA_OVER_FETCH
        )
        analysis_object = get_lab1_analysis_object_from_repositories(repositories)

        logger.debug('Generating analysis of the most famous repositories...')
        self.__graphic_service.create_box_plot(
            file_name='RQ1/RQ1',
            columns=['age'],
            data=analysis_object.get('ages'),
        )
        self.__graphic_service.create_scatter_plot(
            file_name='RQ1/RQ1',
            columns=['age', 'stars'],
            data=analysis_object.get('stars_and_ages'),
        )

        self.__graphic_service.create_box_plot(
            file_name='RQ2/RQ2',
            columns=['prs'],
            data=analysis_object.get('accepted_prs'),
        )
        self.__graphic_service.create_scatter_plot(
            file_name='RQ2/RQ2',
            columns=['prs', 'stars'],
            data=analysis_object.get('stars_and_accepted_prs'),
        )

        self.__graphic_service.create_box_plot(
            file_name='RQ3/RQ3',
            columns=['releases'],
            data=analysis_object.get('total_of_releases'),
        )
        self.__graphic_service.create_scatter_plot(
            file_name='RQ3/RQ3',
            columns=['releases', 'stars'],
            data=analysis_object.get('stars_and_total_of_releases'),
        )

        self.__graphic_service.create_box_plot(
            file_name='RQ4/RQ4',
            columns=['update_freq'],
            data=analysis_object.get('update_frequency'),
        )
        self.__graphic_service.create_scatter_plot(
            file_name='RQ4/RQ4',
            columns=['update_freq', 'stars'],
            data=analysis_object.get('stars_and_update_frequency'),
        )

        languages = analysis_object.get('languages')
        languages = {language: qtd_of_repos for language,qtd_of_repos in languages.items() if language in MOST_FAMOUS_LANGUAGES}
        self.__graphic_service.create_bar_plot(
            file_name='RQ5/RQ5',
            data=[list(languages.keys()), list(languages.values())],
            columns=['languages', 'reopsitories_qtd'],
        )

        self.__graphic_service.create_box_plot(
            file_name='RQ6/RQ6',
            columns=['issues_closed_percent'],
            data=analysis_object.get('percent_of_closed_issues'),
        )
        self.__graphic_service.create_scatter_plot(
            file_name='RQ6/RQ6',
            columns=['issues_closed_percent', 'stars'],
            data=analysis_object.get('stars_and_percent_of_closed_issues'),
        )
        logger.debug('Ended of analysis of the most famous repositories!')
      
