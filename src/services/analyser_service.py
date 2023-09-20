from datetime import date
from multiprocessing import Process
from lch.core.constants import MOST_FAMOUS_LANGUAGES, PREFER_GET_PERSISTED_DATA_OVER_FETCH, TOTAL_QUANTITY_OF_REPOSITORIES
from lch.models.analysis import Lab1AnalysisObject, get_lab1_analysis_object_from_repositories
from lch.models.repository import Repository
from lch.repository.github.github_most_famous_repo_repository import GithubMostFamousRepoRepository
from lch.repository.github.github_most_famous_repo_repository_lab_02 import GithubMostFamousRepoRepositoryLab02
from lch.services.clone_service import CloneService
from lch.services.code_metric_analyser_service import CodeMetricAnalyserService
from lch.services.graphic_service import GraphicService
from lch.shared.date_utils import diff_in_days
from lch.shared.logger import get_logger
from lch.shared.process_utils import create_listener_process, create_queue, maintain_process_alive_while_process_are_running

logger = get_logger(__name__)

class AnalyzerService:
    def __init__(
        self,
        github_most_famous_repo_repositoriy: GithubMostFamousRepoRepository,
        github_most_famous_repo_repositoriy_lab_02: GithubMostFamousRepoRepositoryLab02,
        clone_service: CloneService,
        code_metric_analyser: CodeMetricAnalyserService,
        graphic_service: GraphicService
    ):
        self.__github_most_famous_repo_repositoriy = github_most_famous_repo_repositoriy
        self.__github_most_famous_repo_repositoriy_lab_02 = github_most_famous_repo_repositoriy_lab_02
        self.__clone_service = clone_service
        self.__code_metric_analyser = code_metric_analyser
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
    
    # TODO: REFACTOR REFACTOR REFACTOR
    async def lab_02(self):
        repositories = await self.__github_most_famous_repo_repositoriy_lab_02.get_most_famous_repositories(
            prefer_to_use_persited_repositories=False
        )

        processes: list[Process] = []
        clone_queue = create_queue()
        ck_queue = create_queue()
        analyser_queue = create_queue()

        repositories = [repositories[1], repositories[2]]
        for repository in repositories:
            clone_queue.put_nowait(repository)

        for _ in range(2):
            process = create_listener_process(self.__clone_service.clone_repository, clone_queue, ck_queue)
            process.start()
            processes.append(process)
        for _ in range(3):
            process = create_listener_process(self.__code_metric_analyser.analyse_project, ck_queue, analyser_queue)
            process.start()
            processes.append(process)
            
        maintain_process_alive_while_process_are_running(processes)
        processes.clear()
        for _ in range(2):
            process = create_listener_process(self.__code_metric_analyser.process_data, analyser_queue)
            process.start()
            processes.append(process)
        maintain_process_alive_while_process_are_running(processes)