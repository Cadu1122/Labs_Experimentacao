import asyncio
from repository.data_persistance.data_persistence_repository import DataPersistanceRepository
from repository.github.github_repository import GithubRepository
from shared.graphql_client import GraphqlClient

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