from typing import TypedDict

from lch.shared.dict_shared import safe_get_value


class Repository(TypedDict):
    owner: str
    name: str
    total_of_prs: int

def from_github_response(response: dict):
    result: list[Repository] = []
    data = safe_get_value(response, ('data',), default_value={})
    for value in data.get('search', {}).get('nodes', []):
        name, owner = value.get('nameWithOwner').split('/')
        total_of_prs = value.get('pullRequests', {}).get('totalCount')
        result.append(Repository(name=name, owner=owner, total_of_prs=total_of_prs))
    return result

def from_csv(row: tuple[str], _):
    return Repository(owner=row[0], name=row[1], total_of_prs=int(row[2]))