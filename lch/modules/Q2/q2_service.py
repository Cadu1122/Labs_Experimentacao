from datetime import date
import json
import os
from pathlib import Path
from statistics import median
from time import sleep
from typing import Tuple
from uuid import uuid4
from lch.core.logger import get_logger
from lch.modules.Q2.models.repository import Repository
from lch.modules.analysers.repository_analyser import RepositoryAnalyser
from lch.modules.data_persitance.data_persistance_repository import DataPersistanceRepository
from lch.modules.data_persitance.models.seriale_rules import SerializeRule
from lch.modules.github.models.query_builders.objects.issues_query_builder import IssueStates, IssuesQueryBuilder
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from lch.modules.github.models.query_builders.objects.releases_query_builder import ReleaseOrderByDirection, ReleaseOrderByField, ReleasesQueryBuilder
from lch.modules.github.models.query_builders.objects.repository_query_builder import RepositoryQueryBuilder
from lch.modules.github.models.query_builders.objects.stargazers_query_builder import StargazersQueryBuilder
from lch.modules.github.github_service import GithubService
from lch.shared.date_shared import datetime_str_to_date, diff_in_years
from lch.shared.process_shared import BackgroundMessagersProcessPool, ExecutionType
import shutil

logger = get_logger(__name__)

class Q2Service:
    def __init__(
        self, 
        github_repository: GithubService,
        repository_analyser: RepositoryAnalyser,
        data_persitance_service: DataPersistanceRepository
    ):
        self.__now = date.today()
        self._github_repository = github_repository
        self._repository_analyser = repository_analyser
        self._data_persitance_service = data_persitance_service

        self._resources_base_save_path = 'resources/Q2'
        self._resource_base_clone_path = f'{self._resources_base_save_path}/clone'
        self._resource_base_analysis_path = f'{self._resources_base_save_path}/analysis'
        self._resource_base_result_path = f'{self._resources_base_save_path}/result'
        self._resources_base_clone_error_path = f'{self._resources_base_save_path}/error/clone'
        self._resources_base_analysis_error_path = f'{self._resources_base_save_path}/error/analysis'
        self._resources_base_result_error_path = f'{self._resources_base_save_path}/error/result'
    
    async def execute(self):
        repository_query = self.__get_most_famous_repositories_query()
        search_query = 'stars:>100 language:Java'
        result = []
        repositories = await self._github_repository.search(
            search=search_query,
            query=repository_query,
            quantity_of_itens=1_000,
            custom_mapper=self.__map_repository_response
        )
        for repos in repositories:
            result.extend(repos)
        self._generate_reports(result)
        
      
    def _get_clone_path(self, repository_name: str):
        return Path(f'{self._resource_base_clone_path}/{repository_name}')
    
    def _clone_wrapper(self, repository: Repository):
        repo_name = repository.get('name')
        unique_id = str(uuid4())
        repository['composed_repo_name'] = f'{repo_name}_{unique_id}'
        try:
            logger.debug(f'Repository {repo_name} is being cloned')
            self._github_repository.clone(
                url=repository.get('url'),
                save_path=self._get_clone_path(repository.get('composed_repo_name'))
            )
            logger.debug(f'Repository {repo_name} cloned!')
            return repository
        except Exception as e:
            logger.error(f'Error to clone {repo_name}...', exc_info=True)
            error_path = f'{self._resources_base_clone_error_path}/{repository.get("composed_repo_name")}.json'
            with open(error_path, 'w+') as f:
                error_object = {
                    'repository': repository,
                    'error': str(e)
                }
                f.write(json.dumps(error_object, indent=3))
      
    def _get_analysis_save_path(self, repository_name: str):
        return Path(f'{self._resource_base_analysis_path}/{repository_name}')

    def _analysis_wrapper(self, repository: Repository):
        repo_name = repository.get('name')
        composed_repo_name = repository.get('composed_repo_name')
        repo_path = self._get_clone_path(composed_repo_name)
        save_path = self._get_analysis_save_path(composed_repo_name)
        try:
            logger.debug(f'Analysing repo {repo_name}')
            self._repository_analyser.analyse(repo_path, save_path)
            logger.debug(f'Repo {repo_name} analysed!')
            logger.debug(f'Deleting cloned repo {repo_name}')
            shutil.rmtree(f'{self._get_clone_path(composed_repo_name)}', ignore_errors=True)
            logger.debug(f'Cloned repo {repo_name} deleted')
            return repository
        except Exception as e:
            logger.error(f'Error to analyse {repo_name}...', exc_info=True)
            error_path = f'{self._resources_base_analysis_error_path}/{composed_repo_name}.json'
            with open(error_path, 'w+') as f:
                error_object = {
                    'repository': repository,
                    'error': str(e)
                }
                f.write(json.dumps(error_object, indent=3))
    
    def __get_most_famous_repositories_query(self) -> RepositoryQueryBuilder:
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
        return repository
    
    def __map_repository_response(self, values: dict) -> list[Repository]:
        repositories: list[Repository] = []
        for value in values.get('data').get('search').get('nodes'):
          created_at = datetime_str_to_date(value.get('createdAt'))
          repositories.append(Repository(
              name=value.get('name'),
              url=value.get('url'),
              stars=value.get('total_of_stars').get('totalCount'),
              releases=value.get('releases').get('totalCount'),
              age=diff_in_years(self.__now, created_at)
          ))
        return repositories 

    def _summarize_analysis_response(self, repository: Repository):
        repository_name = repository.get('name')
        composed_repo_name = repository.get('composed_repo_name')
        try:
          class_metric_path = f'{self._get_analysis_save_path(composed_repo_name)}/class.csv'
          logger.debug(f'Summarizing {repository_name}...')
          result = {
              'repo_name': repository_name,
              'releases': repository.get('releases'),
              'stars': repository.get('stars'),
              'age': repository.get('age'),
              'loc': None,
              'dit': None,
              'cbo': None,
              'lcom': None
          }
          metrics_aggregator = {
              'cbo': [],
              'lcom': [],
              'dit': []
          }
          def mapper_function(row_data: Tuple, _):
            if row_data:
                metrics_aggregator['cbo'].append(float(row_data[3]))
                metrics_aggregator['lcom'].append(float(row_data[11]))
                metrics_aggregator['dit'].append(float(row_data[8]))
                if not result.get('loc'):
                    result['loc'] = int(row_data[35])
                else:
                    result['loc'] += int(row_data[35])
          self._data_persitance_service.get_persited_data_in_csv( file_path=class_metric_path, mapper_function=mapper_function)
          metrics_aggregator['cbo'].sort()
          metrics_aggregator['lcom'].sort()
          metrics_aggregator['dit'].sort()
          result['cbo'] = median(metrics_aggregator['cbo']) if metrics_aggregator['cbo'] else None
          result['lcom'] = median(metrics_aggregator['lcom']) if metrics_aggregator['lcom'] else None
          result['dit'] = metrics_aggregator['dit'][len(metrics_aggregator['dit']) - 1] if metrics_aggregator['dit'] else None
          save_data_path = f'{self._resource_base_result_path}/{composed_repo_name}.csv'
          save_columns = [SerializeRule(key, (key, )) for key in result.keys()]
          self._data_persitance_service.persist_data_in_csv(save_data_path, save_columns, [result])
          logger.debug(f'Repo {repository_name} summarized!')
        except Exception as e:
            logger.error(f'Error to summarize {repository_name}', exc_info=True)
            error_path = f'{self._resources_base_analysis_error_path}/{composed_repo_name}.json'
            with open(error_path, 'w+') as f:
                error_object = {
                    'repository': repository,
                    'error': str(e)
                }
                f.write(json.dumps(error_object, indent=3))

    def _aggregate_summarizations(self):
        aggregated_data = []
        def mapper_function(row_data, columns):
            result = {}
            for i,column in enumerate(columns):
                result[column] = row_data[i]
            aggregated_data.append(result)

        for summarized_file in os.listdir(self._resource_base_result_path):
            file_path =  f'{self._resource_base_result_path}/{summarized_file}'
            self._data_persitance_service.get_persited_data_in_csv(Path(file_path), mapper_function)
        save_path = Path(f'{self._resources_base_save_path}/final_result.csv')
        save_columns = [SerializeRule(key, (key, )) for key in aggregated_data[0].keys()]
        self._data_persitance_service.persist_data_in_csv(save_path, save_columns, aggregated_data)

    def _generate_reports(
        self, 
        repositories: list[Repository], 
        to_be_cloned: list[Repository] = None, 
        to_be_analysed: list[Repository] = None,
        to_generate_result: list[Repository] = None
    ):
        with BackgroundMessagersProcessPool(max_number_of_process=8) as background_p_manager:
            summarizer_queue_name = 'SUMMARIZER_QUEUE'
            clone_queue_name = 'CLONE_QUEUE'
            ck_queue_name = 'CK_QUEUE'
            background_p_manager.define_queue(summarizer_queue_name)
            background_p_manager.define_queue(clone_queue_name)
            background_p_manager.define_queue(ck_queue_name)
            if to_be_cloned:
                background_p_manager.publish_to_queue(clone_queue_name, to_be_cloned)
            else:
                background_p_manager.publish_to_queue(clone_queue_name, repositories)
            if to_be_analysed:
                background_p_manager.publish_to_queue(ck_queue_name, to_be_analysed)
            if to_generate_result:
                background_p_manager.publish_to_queue(summarizer_queue_name, to_be_analysed)
            for _ in range(2):
                background_p_manager.start_process(
                    function=self._clone_wrapper,
                    execution_type=ExecutionType.CONSUMER_PRODUCER,
                    consumer_queue_name=clone_queue_name,
                    producer_queue_name=ck_queue_name
                )
            sleep(15)
            for _ in range(4):
                background_p_manager.start_process(
                    function=self._analysis_wrapper,
                    execution_type=ExecutionType.CONSUMER_PRODUCER,
                    consumer_queue_name=ck_queue_name,
                    producer_queue_name=summarizer_queue_name
                )
            sleep(20)
            for _ in range(2):
                background_p_manager.start_process(
                  function=self._summarize_analysis_response,
                  execution_type=ExecutionType.CONSUMER,
                  consumer_queue_name=summarizer_queue_name
                )
        self._aggregate_summarizations()
    
    def _get_repositorires_from_error_dir(self, path: str):
        repositories = []
        for error_file_name in os.listdir(path):
            error_file_path = f'{path}/{error_file_name}'
            with open(error_file_path) as f:
                repo = json.load(f)
                repositories.append(repo.get('repository'))
        return repositories

    def retry_errors(self):
        to_be_cloned_repos = self._get_repositorires_from_error_dir(self._resources_base_clone_error_path)
        to_be_analysed = self._get_repositorires_from_error_dir(self._resources_base_analysis_error_path)
        to_generate_result = self._get_repositorires_from_error_dir(self._resources_base_result_error_path)
        self._generate_reports(
            repositories=[],
            to_be_analysed=to_be_analysed,
            to_generate_result=to_generate_result,
            to_be_cloned=to_be_cloned_repos
        )