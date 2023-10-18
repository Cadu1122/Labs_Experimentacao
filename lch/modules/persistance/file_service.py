from pathlib import Path
from typing import Any, Callable
import os


class FileService:

    def get_data_from_file(
        self, 
        file_path: Path, 
        custom_mapper: Callable[[str], Any] = lambda value: value
    ):
        data = []
        with open(file_path) as f:
            for line in f.readlines():
                data.append(custom_mapper(line))
        return data
    
    def ensure_path_existence(self, file_path: Path):
        if not file_path.exists():
            if file_path.is_file():
                created_file = open(file_path, 'w+')
                created_file.close()
            else:
                file_path.mkdir()