from enum import Enum, auto


class ClassContainer:
    class Classes(Enum):
        GRAPHQL_CLIENT = auto()
        ANALYZER_SERVICE = auto()
        GITHUB_REPOSITORY = auto()
        GRAPHIC_SERVICE = auto()
        DATA_PERSISTANCE_REPOSITORY = auto()

    __instances: dict[Classes, any] = {}

    def get_analyzer_service(self):
        from projeto_1.services.analyser_service import AnalyzerService
        service: AnalyzerService = self.__instances.get(self.Classes.ANALYZER_SERVICE)
        if not service:
            service = AnalyzerService(
                github_most_famous_repo_repositoriy=self.__get_github_repository(),
                graphic_service=self.__get_graphic_service()
            )
            self.__instances[self.Classes.ANALYZER_SERVICE] = service
        return service
    
    def __get_graphic_service(self):
        from projeto_1.services.graphic_service import GraphicService
        service: GraphicService = self.__instances.get(self.Classes.GRAPHIC_SERVICE)
        if not service:
            service = GraphicService()
            self.__instances[self.Classes.GRAPHIC_SERVICE] = service
        return service

    def __get_github_repository(self):
        from projeto_1.repository.github.github_most_famous_repo_repository import GithubMostFamousRepoRepository
        repository: GithubMostFamousRepoRepository = self.__instances.get(self.Classes.GITHUB_REPOSITORY)
        if not repository:
            repository = GithubMostFamousRepoRepository(
                data_persistance_repository=self.__get_data_persitance_repository(),
                graphql_client=self.__get_graphql_client()
            )
            self.__instances[self.Classes.GITHUB_REPOSITORY] = repository
        return repository
    
    def __get_data_persitance_repository(self):
        from projeto_1.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
        repository: DataPersistanceRepository = self.__instances.get(self.Classes.DATA_PERSISTANCE_REPOSITORY)
        if not repository:
            repository = DataPersistanceRepository()
            self.__instances[self.Classes.DATA_PERSISTANCE_REPOSITORY] = repository
        return repository

    def __get_graphql_client(self):
        from projeto_1.shared.graphql_client import GraphqlClient
        client: GraphqlClient = self.__instances.get(self.Classes.GRAPHQL_CLIENT)
        if not client:
            client = GraphqlClient()
            self.__instances[self.Classes.GRAPHQL_CLIENT] = client
        return client