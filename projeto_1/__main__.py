import asyncio
from projeto_1.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
from projeto_1.repository.github.github_repository import GithubRepository
from projeto_1.shared.graphql_client import GraphqlClient

grapql_client = GraphqlClient()
data_persistance_repository = DataPersistanceRepository()
github_repository = GithubRepository(
    graphql_client=grapql_client,
    data_persistance_repository=data_persistance_repository
)

asyncio.run(
    github_repository.get_most_famous_repositories(
        qtd_of_repositories=100,
        prefer_to_use_persited_repositories=False
    )
)