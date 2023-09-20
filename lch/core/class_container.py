from enum import Enum, auto
from typing import Any

class ClassContainer:
    class Classes(Enum):
        QUESTION_1_SERVICE = auto()

    __instances: dict[Classes, Any] = {}

    def get_question_1_service(self):
        ...