from lch.modules.github.github_service import GithubService
from lch.modules.persistance.csv_service import CsvService
from lch.shared.process_shared import BackgroundMessagersProcessPool


class Q2Service:
    def __init__(
        self,
        github_service: GithubService,
        csv_service: CsvService
    ):
        self.__github_service = github_service
    
    def execute(self):
        ...
    
    def __get_repositories(self):
        ...