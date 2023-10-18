from datetime import date, datetime
from pathlib import Path
from typing import Any
from lch.core.config.constants import MOST_FAMOUS_LANGUAGES
from lch.core.logger import get_logger
from lch.modules.github.models.query_builders.objects.issues_query_builder import IssueStates, IssuesQueryBuilder
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from lch.modules.github.models.query_builders.objects.releases_query_builder import ReleaseOrderByDirection, ReleaseOrderByField, ReleasesQueryBuilder
from lch.modules.github.models.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.modules.github.models.query_builders.objects.stargazers_query_builder import StargazersQueryBuilder
from lch.modules.github.github_service import GithubService
from lch.modules.graphic.graphic_service import GraphicService
from lch.modules.persistance.csv_service import CsvService
from lch.modules.persistance.file_service import FileService
from lch.modules.persistance.models.serialize_rules import SerializeRule
from lch.modules.questions.question_1.models.repository import Repository
from lch.modules.questions.question_1.models.repository_analysis import get_analysis_object_from_repositories
from lch.shared.date_shared import datetime_str_to_date, str_to_datetime
from lch.shared.dict_shared import safe_get_value
from lch.shared.list_shared import flat_map

logger = get_logger(__name__)

class Q1Service:
    def __init__(
        self, 
        graphic_service: GraphicService,
        github_service: GithubService,
        file_service: FileService,
        csv_service: CsvService
    ):
        self.__graphic_service = graphic_service
        self.__github_service = github_service
        self.__file_service = file_service
        self.__csv_service = csv_service

        self.__base_resource_path = 'resource/RQ1'
        self.__rq1_path = Path(f'{self.__base_resource_path}/Q1/')
        self.__rq2_path = Path(f'{self.__base_resource_path}/Q2/')
        self.__rq3_path = Path(f'{self.__base_resource_path}/Q3/')
        self.__rq4_path = Path(f'{self.__base_resource_path}/Q4/')
        self.__rq5_path = Path(f'{self.__base_resource_path}/Q5/')
        self.__rq6_path = Path(f'{self.__base_resource_path}/Q6/')
    
    async def execute(self, use_persisted_repositories: bool = False):
        repositories = await self.__get_repositories(
            use_persisted_repositories=use_persisted_repositories
        )
        self.__ensure_all_necessary_paths_exist()
        self.__generate_graphics_to_question(repositories)

    
    async def __get_repositories(self, use_persisted_repositories: bool):
        if use_persisted_repositories:
            return self.__get_persisted_repositories()
        repository_query = self.__mount_query()
        search = 'stars:>100'
        repositories: list[list[Repository]] = await self.__github_service.search(
            search=search,
            query=repository_query,
            quantity_of_itens=1_000,
            custom_mapper=self.__handle_query_response
        )
        repositories = flat_map(repositories)
        self.__persit_repositories(repositories)
        self.__generate_graphics_to_question(repositories)
        
    
    def __get_persisted_repositories(self):
        results: list[Repository] = []
        path = Path(f'{self.__base_resource_path}/repositories.csv')
        def mapper(row: tuple, columns: tuple):
            results.append(
                Repository(
                    name=row[0],
                    created_at=date.fromisoformat(row[1]),
                    merged_prs=int(row[2]),
                    stars=int(row[3]),
                    closed_issues=int(row[4]),
                    total_of_issues=int(row[5]),
                    last_update_date=datetime.fromisoformat(row[6]),
                    primary_language=row[7],
                    total_of_releases=int(row[8])
                )
            )
        self.__csv_service.get_persited_data_in_csv(
            file_path=path,
            mapper_function=mapper
        )
        return results
    
    def __mount_query(self) -> RepositoryQueryBuilder:
        logger.debug('Mouting query to obtain repositories')
        repository = RepositoryQueryBuilder(
            has_created_at=True,
            has_name=True,
            has_primary_language=True,
            has_updated_at=True,
            has_url=True
        )
        repository.compose_with_query(
          IssuesQueryBuilder(
            has_total_count=True,
            state=IssueStates.CLOSED
          ),
          custom_attr='total_of_closed_issues'
        )
        repository.compose_with_query(
          IssuesQueryBuilder(
            has_total_count=True,
          ),
          custom_attr='total_of_issues'
        )
        repository.compose_with_query(
          PullRequestsQueryBuilder(
            has_total_count=True,
            state=PullRequestsState.MERGED
          )
        )
        repository.compose_with_query(
          ReleasesQueryBuilder(
            has_total_count=True,
            order_by_field=ReleaseOrderByField.CREATED_AT,
            oder_by_direction=ReleaseOrderByDirection.DESC
          )
        )
        repository.compose_with_query(
            StargazersQueryBuilder(
              has_total_count=True
            ),
            custom_attr='total_of_stars'
        )
        logger.debug('Query mounted!')
        return repository
  
    def __handle_query_response(self, response: list[dict[str, Any]]):
        repositories: list[Repository] = []
        get_total_count_from_attr = lambda value, attr: value.get(attr).get('totalCount')
        data = safe_get_value(response, ('data',), default_value={})
        for value in data.get('search', {}).get('nodes', []):
            primary_language =  safe_get_value(value, ('primaryLanguage', 'name'))
            repositories.append(Repository(
                name=value.get('name'),
                created_at=datetime_str_to_date(value.get('createdAt')),
                primary_language=primary_language,
                closed_issues=get_total_count_from_attr(value, 'total_of_closed_issues'),
                total_of_issues=get_total_count_from_attr(value, 'total_of_issues'),
                merged_prs=get_total_count_from_attr(value, 'pullRequests'),
                total_of_releases=get_total_count_from_attr(value, 'releases'),
                last_update_date=str_to_datetime(value.get('updatedAt')),
                stars=get_total_count_from_attr(value, 'total_of_stars')
            ))
        return repositories

    def __persit_repositories(self, repositories: list[Repository]):
        columns = (
            SerializeRule(column_name='name', dict_deserialize_rule=('name',)),
            SerializeRule(column_name='created_at', dict_deserialize_rule=('created_at',)),
            SerializeRule(column_name='merged_prs', dict_deserialize_rule=('merged_prs',)),
            SerializeRule(column_name='total_of_stars', dict_deserialize_rule=('stars',)),
            SerializeRule(column_name='total_of_closed_issues', dict_deserialize_rule=('closed_issues',)),
            SerializeRule(column_name='total_of_issues', dict_deserialize_rule=('total_of_issues',)),
            SerializeRule(column_name='last_update_date', dict_deserialize_rule=('last_update_date',)),
            SerializeRule(column_name='primary_language', dict_deserialize_rule=('primary_language',)),
            SerializeRule(column_name='total_of_releases', dict_deserialize_rule=('total_of_releases',)),
        )
        self.__csv_service.persist_data_in_csv(
            file_path=Path('resources/Q1/repositories.csv'),
            columns=columns,
            data=repositories
        )

    def __ensure_all_necessary_paths_exist(self):
        self.__file_service.ensure_path_existence(Path(self.__rq1_path))
        self.__file_service.ensure_path_existence(Path(self.__rq2_path))
        self.__file_service.ensure_path_existence(Path(self.__rq3_path))
        self.__file_service.ensure_path_existence(Path(self.__rq4_path))
        self.__file_service.ensure_path_existence(Path(self.__rq5_path))

    def __generate_graphics_to_question(self, repositories: list[Repository]):
        analysis_object = get_analysis_object_from_repositories(repositories)

        logger.debug('Generating analysis of the most famous repositories...')

        rq1_path_box_plot = self.__rq1_path.joinpath('RQ1_BOX_PLOT')
        self.__graphic_service.create_box_plot(
            file_path=rq1_path_box_plot,
            columns=['age'],
            data=analysis_object.get('ages'),
        )
        rq1_path_scatter_plot = self.__rq1_path.joinpath('RQ1_SCATTER_PLOT')
        self.__graphic_service.create_scatter_plot(
            file_path=rq1_path_scatter_plot,
            columns=['age', 'stars'],
            data=analysis_object.get('stars_and_ages'),
        )

        rq2_path_box_plot = self.__rq2_path.joinpath('RQ2_BOX_PLOT')
        self.__graphic_service.create_box_plot(
            file_path=rq2_path_box_plot,
            columns=['prs'],
            data=analysis_object.get('accepted_prs'),
        )
        rq2_path_scatter_plot = self.__rq2_path.joinpath('RQ2_SCATTER_PLOT')
        self.__graphic_service.create_scatter_plot(
            file_path=rq2_path_scatter_plot,
            columns=['prs', 'stars'],
            data=analysis_object.get('stars_and_accepted_prs'),
        )

        rq3_path_box_plot = self.__rq3_path.joinpath('RQ3_BOX_PLOT')
        self.__graphic_service.create_box_plot(
            file_path=rq3_path_box_plot,
            columns=['releases'],
            data=analysis_object.get('total_of_releases'),
        )
        rq3_path_scatter_plot = self.__rq3_path.joinpath('RQ3_SCATTER_PLOT')
        self.__graphic_service.create_scatter_plot(
            file_path=rq3_path_scatter_plot,
            columns=['releases', 'stars'],
            data=analysis_object.get('stars_and_total_of_releases'),
        )

        rq4_path_box_plot = self.__rq4_path.joinpath('RQ4_BOX_PLOT')
        self.__graphic_service.create_box_plot(
            file_path=rq4_path_box_plot,
            columns=['update_freq'],
            data=analysis_object.get('update_frequency'),
        )
        rq4_path_scatter_plot = self.__rq4_path.joinpath('RQ4_SCATTER_PLOT')
        self.__graphic_service.create_scatter_plot(
            file_path=rq4_path_scatter_plot,
            columns=['update_freq', 'stars'],
            data=analysis_object.get('stars_and_update_frequency'),
        )
        
        languages = analysis_object.get('languages')
        languages = {language: qtd_of_repos for language,qtd_of_repos in languages.items() if language in MOST_FAMOUS_LANGUAGES}
        rq5_path_box_plot = self.__rq5_path.joinpath('RQ5_BOX_PLOT')
        self.__graphic_service.create_bar_plot(
            file_path=rq5_path_box_plot,
            data=[list(languages.keys()), list(languages.values())],
            columns=['languages', 'reopsitories_qtd'],
        )
        rq5_path_scatter_plot = self.__rq5_path.joinpath('RQ5_SCATTER_PLOT')
        self.__graphic_service.create_box_plot(
            file_path=rq5_path_scatter_plot,
            columns=['issues_closed_percent'],
            data=analysis_object.get('percent_of_closed_issues'),
        )

        rq6_path_scatter_plot = self.__rq6_path.joinpath('RQ6_SCATTER_PLOT') 
        self.__graphic_service.create_scatter_plot(
            file_path=rq6_path_scatter_plot,
            columns=['issues_closed_percent', 'stars'],
            data=analysis_object.get('stars_and_percent_of_closed_issues'),
        )
        logger.debug('Ended of analysis of the most famous repositories!')