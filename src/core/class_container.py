from enum import Enum, auto


class ClassContainer:
    class Classes(Enum):
        GRAPHQL_CLIENT = auto()
        ANALYZER_SERVICE = auto()
        GITHUB_REPOSITORY = auto()
        GITHUB_REPOSITORY_LAB_O2 = auto()
        GRAPHIC_SERVICE = auto()
        DATA_PERSISTANCE_REPOSITORY = auto()
        CLONE_SERVICE = auto()
        CODE_METRIC_ANALYSER_SERVICE = auto()

    __instances: dict[Classes, any] = {}

    def get_analyzer_service(self):
        from src.services.analyser_service import AnalyzerService
        service: AnalyzerService = self.__instances.get(self.Classes.ANALYZER_SERVICE)
        if not service:
            service = AnalyzerService(
                github_most_famous_repo_repositoriy=self.__get_github_repository(),
                github_most_famous_repo_repositoriy_lab_02=self.__get_github_repository_lab_02(),
                clone_service=self.get_clone_service(),
                code_metric_analyser=self.get_code_analysis_service(),
                graphic_service=self.__get_graphic_service()
            )
            self.__instances[self.Classes.ANALYZER_SERVICE] = service
        return service

    def get_clone_service(self):
        from src.services.clone_service import CloneService
        service: CloneService = self.__instances.get(self.Classes.CLONE_SERVICE)
        if not service:
            service = CloneService()
            self.__instances[self.Classes.CLONE_SERVICE] = service
        return service
    
    def get_code_analysis_service(self):
        from src.services.code_metric_analyser_service import CodeMetricAnalyserService
        service: CodeMetricAnalyserService = self.__instances.get(self.Classes.CODE_METRIC_ANALYSER_SERVICE)
        if not service:
            service = CodeMetricAnalyserService(
                data_persistance_repository=self.__get_data_persitance_repository()
            )
            self.__instances[self.Classes.CODE_METRIC_ANALYSER_SERVICE] = service
        return service
    
    def __get_graphic_service(self):
        from src.services.graphic_service import GraphicService
        service: GraphicService = self.__instances.get(self.Classes.GRAPHIC_SERVICE)
        if not service:
            service = GraphicService()
            self.__instances[self.Classes.GRAPHIC_SERVICE] = service
        return service

    def __get_github_repository(self):
        from src.repository.github.github_most_famous_repo_repository import GithubMostFamousRepoRepository
        repository: GithubMostFamousRepoRepository = self.__instances.get(self.Classes.GITHUB_REPOSITORY)
        if not repository:
            repository = GithubMostFamousRepoRepository(
                data_persistance_repository=self.__get_data_persitance_repository(),
                graphql_client=self.__get_graphql_client()
            )
            self.__instances[self.Classes.GITHUB_REPOSITORY] = repository
        return repository

    def __get_github_repository_lab_02(self):
        from src.repository.github.github_most_famous_repo_repository_lab_02 import GithubMostFamousRepoRepositoryLab02
        repository: GithubMostFamousRepoRepositoryLab02 = self.__instances.get(self.Classes.GITHUB_REPOSITORY_LAB_O2)
        if not repository:
            repository = GithubMostFamousRepoRepositoryLab02(
                data_persistance_repository=self.__get_data_persitance_repository(),
                graphql_client=self.__get_graphql_client()
            )
            self.__instances[self.Classes.GITHUB_REPOSITORY_LAB_O2] = repository
        return repository
    
    def __get_data_persitance_repository(self):
        from src.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
        repository: DataPersistanceRepository = self.__instances.get(self.Classes.DATA_PERSISTANCE_REPOSITORY)
        if not repository:
            repository = DataPersistanceRepository()
            self.__instances[self.Classes.DATA_PERSISTANCE_REPOSITORY] = repository
        return repository

    def __get_graphql_client(self):
        from src.shared.graphql_client import GraphqlClient
        client: GraphqlClient = self.__instances.get(self.Classes.GRAPHQL_CLIENT)
        if not client:
            client = GraphqlClient()
            self.__instances[self.Classes.GRAPHQL_CLIENT] = client
        return client