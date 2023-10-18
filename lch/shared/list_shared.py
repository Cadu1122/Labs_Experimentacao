from typing import Any


def flat_map(values: list[list[Any]]):
    return [item for items in values for item in items]