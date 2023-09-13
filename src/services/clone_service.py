import os
from subprocess import run
from typing import Tuple
from uuid import uuid4
from src.core.constants import CLONED_REPOSITORIES_PATH
from src.models.repository import RepositoryLab02

class CloneService:
    def clone_repository(self, repository: RepositoryLab02) -> Tuple[str, RepositoryLab02]:
        default_branch = 'main'
        repo_name = repository.get("name")
        repo_name = repo_name if repo_name else str(uuid4())
        directory_path = f'{CLONED_REPOSITORIES_PATH}/{repo_name}'
        command = f'''
            git clone \
                --quiet --no-tags \
                --branch {{default_branch}} --single-branch \
                --depth=1 {repository.get('url')} {directory_path}
        '''
        try:
            formatted_command = command.format_map({'default_branch': default_branch})
            run(formatted_command, shell=True, check=True)
            return directory_path, repository
        except Exception as e:
            default_branch = 'master'
            formatted_command = command.format_map({'default_branch': default_branch})
            run(formatted_command, shell=True, check=True)
            return directory_path, repository