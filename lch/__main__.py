import asyncio
from lch.core.graphql_client import GraphqlClient
from lch.domain.Q2.q2_service import Q2Service
from lch.domain.analysers.repository_analyser import RepositoryAnalyser
from lch.domain.auth.service.auth_service import AuthService
from lch.domain.data_persitance.data_persistance_repository import DataPersistanceRepository
from lch.domain.file.service.file_service import FileService
from lch.domain.github.repository.github_repository import GithubRepository

gq_cli = GraphqlClient()
fc_service = FileService()
auth_service = AuthService(file_service=fc_service)
gh_repo = GithubRepository(
    graphql_client=gq_cli,
    auth_service=auth_service
)
repo_ana = RepositoryAnalyser()
data_repo = DataPersistanceRepository()
q2_service = Q2Service(
    github_repository=gh_repo,
    repository_analyser=repo_ana,
    data_persitance_service=data_repo
)

asyncio.run(q2_service.execute())
