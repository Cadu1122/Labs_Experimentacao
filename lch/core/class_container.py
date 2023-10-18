from enum import Enum, auto
from typing import Any

class ClassContainer:
    class __Classes(Enum):
        QUESTION_1_SERVICE = auto()
        QUESTION_2_SERVICE = auto()
        GITHUB_REPOSITORY = auto()
        GRAPHQL_CLIENT = auto()
        FILE_SERVICE = auto()

    __instances: dict[__Classes, Any] = {}

    def get_question_1_service(self):
        from lch.modules.questions.question_1.q1_service import Q1Service
        key = self.__Classes.QUESTION_1_SERVICE
        service = self.__instances.get(key)
        if not service:
            service = Q1Service(
                github_repository=self.__get_github_repository()
            )
            self.__instances[key] = service
        return service
    
    def __get_github_repository(self):
        from lch.modules.github.github_service import GithubService
        key = self.__Classes.GITHUB_REPOSITORY
        service = self.__instances.get(key)
        if not service:
            service = GithubService(
                graphql_client=self.__get_graphql_client(),
                file_service=self.__get_file_service()
            )
            self.__instances[key] = service
        return service

    def __get_graphql_client(self):
        from lch.core.clients.graphql_client import GraphqlClient
        key = self.__Classes.GRAPHQL_CLIENT
        service = self.__instances.get(key)
        if not service:
            service = GraphqlClient()
            self.__instances[key] = service
        return service

    def __get_file_service(self):
        from lch.modules.persistance.file_service import FileService
        key = self.__Classes.FILE_SERVICE
        service = self.__instances.get(key)
        if not service:
            service = FileService()
            self.__instances[key] = service
        return service