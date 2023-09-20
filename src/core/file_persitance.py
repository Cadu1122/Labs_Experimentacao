import os
from pathlib import Path

from lch.core.constants import DEBUG_PATH, GRAPHIC_PATH, REPOSITORIES_PATH


def ensure_all_necessary_paths_exist():
    debug_path = Path(DEBUG_PATH)
    repositories_path = Path(REPOSITORIES_PATH)
    graphic_path = Path(GRAPHIC_PATH)

    __ensure_path_existance(debug_path)
    __ensure_path_existance(repositories_path)
    __ensure_path_existance(graphic_path)

def __ensure_path_existance(path: Path):
    if not path.exists():
        if path.is_file():
            f = open(path, 'w+')
            f.close()
        else:
            os.mkdir(path)