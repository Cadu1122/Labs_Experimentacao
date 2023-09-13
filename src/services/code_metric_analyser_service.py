import os
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from src.core.constants import REPO_ANALYSIS_PATH
from subprocess import run

from src.models.repository import RepositoryLab02
from src.repository.data_persistance.data_persistence_repository import DataPersistanceRepository
from src.repository.data_persistance.models.serialize_rules import SerializeRule

class CodeMetricAnalyserService:
    def __init__(self, data_persistance_repository: DataPersistanceRepository):
        self.__data_persistance_repository = data_persistance_repository

    def analyse_project(self, data: Tuple[str, RepositoryLab02]) -> Tuple[str, RepositoryLab02]:
        try:
            repo = data[1]
            project_path = data[0]
            repo_name = repo.get('name')
            analysis_result_path = f'{REPO_ANALYSIS_PATH}/{repo_name}/'
            os.mkdir(analysis_result_path)
            run(f'java -jar ck.jar {project_path} false 0 False {analysis_result_path}', shell=True, check=True)
            return analysis_result_path, repo
        except Exception as e:
            print(e)
            raise e
    
    def process_data(self, data: Tuple[str, RepositoryLab02]) -> Tuple[str, RepositoryLab02]:
        repository = data[1]
        class_metric_path = Path(f'{data[0]}/class.csv')
        result = {
            'repo_name': repository.get('name'),
            'releases': repository.get('total_of_releases'),
            'age': repository.get('age_in_years'),
            'loc': 0,
            'cbo': 0,
            'lcom': 0
        }
        def mapper_function(row_data: Tuple, _):
            if row_data:
                result['loc'] += int(row_data[35])
                result['cbo'] += int(row_data[3])
                result['lcom'] += int(row_data[11])

        self.__data_persistance_repository.get_persited_data_in_csv(class_metric_path, mapper_function)
        save_data_path = f"resources/lab02_results/{repository.get('name')}.csv" 
        save_columns = [SerializeRule(key, (key, )) for key in result.keys()]
        self.__data_persistance_repository.persist_data_in_csv(save_data_path, save_columns, [result])
