import os
from pathlib import Path
from subprocess import run

from lch.core.logger import get_logger

logger = get_logger(__name__)

class RepositoryAnalyser:

    def analyse(
        self, 
        repository_path: Path, 
        analysis_save_path: Path
    ):
        try:
            repository_path = repository_path.as_posix()
            analysis_save_path = f'{analysis_save_path.as_posix()}/'
            if not Path(analysis_save_path).exists():
                os.mkdir(analysis_save_path)
            logger.debug(f'Analysing repository present in {repository_path}')
            run(f'java -jar ck.jar {repository_path} false 0 False {analysis_save_path}', shell=True, check=True)
        except Exception as e:
            logger.error('Error to analyse repository', exc_info=True)
            raise e