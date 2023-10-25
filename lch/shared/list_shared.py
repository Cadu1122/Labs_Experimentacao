from typing import Any


def flat_map(values: list[list[Any]]):
    return [item for items in values for item in items]

def chunk_list(values: list[str], chunks_size=5):
    for i in range(0, len(values), chunks_size):
        yield values[i:i + chunks_size]

def partiiton_list(values: list[Any], partition_idx: int):
    a,b = [], []
    for i, value in enumerate(values):
        if i < partition_idx:
            a.append(value)
        else:
            b.append(value)
    return a,b