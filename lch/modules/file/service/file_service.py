from pathlib import Path
from typing import Any, Callable


class FileService:

    def get_data_from_file(
        self, 
        file_path: Path, 
        custom_mapper: Callable[[str], Any] = lambda value: value
    ):
        data = []
        with open(file_path) as f:
            data.append(custom_mapper(f.readline()))
        return data
    
    def ensure_path_existence(self, file_path: Path):
        if not file_path.exists():
            raise ValueError('File does not exist...')