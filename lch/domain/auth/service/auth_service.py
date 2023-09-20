from pathlib import Path
from lch.core.constants import GITHUB_TOKEN_PATH
from lch.domain.file.service.file_service import FileService


class AuthService:
    def __init__(self, file_service: FileService):
        self.__file_service = file_service
        self.__github_token: str = None

    def get_github_token(self) -> str:
        if not self.__github_token:
            self.__github_token = self.__file_service.get_data_from_file(
                file_path=Path(GITHUB_TOKEN_PATH)
            )[0]
        return self.__github_token