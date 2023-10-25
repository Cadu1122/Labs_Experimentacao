# from datetime import datetime
# from functools import reduce
# import json
# from typing import TypedDict
# from lch.core.class_container import ClassContainer
# from lch.core.config.constants import GITHUB_AUTH_TOKEN_V2_PATH, MAX_REQUESTS_PER_HOUR_IN_GITHUB
# from lch.modules.github.models.token import TokenInfo
# from lch.modules.questions.question_3.models.repository import Repository
# from lch.shared.date_shared import diff_in_hours, str_to_datetime
# from lch.shared.process_shared import BackgroundMessagersProcessPool

# # class RepositoryPreparedQuery(TypedDict):


# class_container = ClassContainer()
# q3_service = class_container.get_question_3_service()

# def get_disponible_tokens():
#     disponible_tokens: list[tuple[dict[str, TokenInfo], int]] = []
#     some_token_was_founded = False
#     while not some_token_was_founded:
#         now = datetime.now()
#         tokens: dict[str, TokenInfo] = {}
#         with open(GITHUB_AUTH_TOKEN_V2_PATH) as f:
#             tokens = json.load(f)
#         for key, tk_info in tokens.items():
#             last_use = str_to_datetime(tk_info.get('last_use'))
#             if diff_in_hours(now, last_use) > 1:
#                 tk_info['qtd_of_requests_made'] = 0
#                 disponible_tokens.append(({key: tk_info}, MAX_REQUESTS_PER_HOUR_IN_GITHUB))
#                 some_token_was_founded = True
#             elif tk_info.get('qtd_of_requests_made') < MAX_REQUESTS_PER_HOUR_IN_GITHUB:
#                 remaining_queries = MAX_REQUESTS_PER_HOUR_IN_GITHUB - tk_info.get('qtd_of_requests_made')
#                 tk_info['qtd_of_requests_made'] += remaining_queries
#                 disponible_tokens.append(({key: tk_info}, remaining_queries))
#                 some_token_was_founded = True
#     return disponible_tokens

# async def send_data_to_be_fetched():
#     repositories = await q3_service.get_famous_repositories()
#     for repository in repositories:
#         queries = q3_service.get_all_possible_queries_per_repo(repository)
#         remaining_queries = repository.get('total_of_prs')
#         should_maintain_repo_context = True
#         while should_maintain_repo_context:
#             if remaining_queries == 0:
#                 should_maintain_repo_context = False
#             else:
#                 tokens = get_disponible_tokens()
#                 last_query_evaluated_idx = 0
#                 for token_data in tokens:
#                     queries_per_token = queries[last_query_evaluated_idx::token_data[1]]
#                     last_query_evaluated_idx += token_data
#                 # total_of_queries_disponible = reduce(lambda a, b: a + b, [value[1] for value in tokens])
#                 # yield

import asyncio
import base64
import csv
from datetime import datetime
import json
import os
from pathlib import Path
from time import sleep
from typing import TypedDict
from lch.core.class_container import ClassContainer
from lch.core.config.constants import MAX_REQUESTS_TO_GITHUB
from lch.core.logger import get_logger
from lch.modules.github.models.query_builders.functions.repository_function_query_builder import RepositoryFunctionQueryBuilder
from lch.modules.github.models.query_builders.objects.pull_requests_query_builder import PullRequestsQueryBuilder, PullRequestsState
from lch.modules.questions.question_3.models.repository import Repository
from lch.shared.date_shared import diff_in_hours
from lch.shared.dict_shared import safe_get_value
from lch.shared.exceptions.grapql_client_exceptions import SomethingException
from lch.shared.list_shared import chunk_list, partiiton_list
from src.core.constants import QUERIES_CHUNK_SIZE


class TokenInfo(TypedDict):
    token: str
    last_use: datetime | None
    requests_made: int

class Pr(TypedDict):
    created_at: str
    merged_at: str
    closed_at: str
    deletion_count: int
    additions_count: int
    body: str
    comment_count: int
    participants_count: int

TOKENS: dict[str, TokenInfo] = {
    'aa97f7f9-062c-470e-b9f0-adcff3bc1683': {
        'token': '',
        'last_use': datetime.now(),
        'requests_made': 0
    },
    'fada7b07-b6be-4724-aa50-fd1b4db27386': {
        'token': '',
        'last_use': datetime.now(),
        'requests_made': 0 
    }
}
BASE_PERSISTANCE_PATH = 'resources/RQ3/data/repo_pr'
PR_CSV_COLUMNS = ('created_at','merged_at','closed_at','deletion_count','additions_count','body','comment_count','participants_count')
BLACKLIST_REPOS = os.listdir(BASE_PERSISTANCE_PATH)

logger = get_logger(__name__)

pr_default_query = PullRequestsQueryBuilder(
    has_additions_count=True,
    has_body=True,
    has_closed_at=True,
    has_comment_count=True,
    has_deletion_count=True,
    has_merged_at=True,
    has_participants_count=True,
    has_created_at=True,
    state=[PullRequestsState.MERGED, PullRequestsState.CLOSED],
    quantity_of_itens_per_query=50
)

def get_repository_query(repository: Repository):
    repository_query = RepositoryFunctionQueryBuilder(
        owner=repository.get('owner'), 
        name=repository.get('name')
    )
    repository_query.with_pr(pr_default_query)
    return repository_query

def mount_every_possible_query_for_repositories(repositories: list[Repository]):
    class_manager = ClassContainer()
    q3_service = class_manager.get_question_3_service()
    queries_per_repository: list[tuple(Repository, list[str])] = []
    for repository in repositories:
        queries = q3_service.get_all_possible_queries_per_repo(repository)
        queries_per_repository.append((repository, queries))
    return queries_per_repository

def order_repos_queries_exec_by_qtd(repo_query: list[tuple[Repository, list[str]]]):
    def sort_key(value: tuple[Repository, list[str]]):
        return len(value[1])
    logger.debug('Sorting repositories by quantity of query')
    return sorted(repo_query, key=sort_key)

def get_disponible_token(qtd_of_requests: int):
    logger.debug('Getting disponible tokens to make requests')
    is_token_founded = False
    while not is_token_founded:
        now = datetime.now()
        for key, token in TOKENS.items():
            disp_req = MAX_REQUESTS_TO_GITHUB - token.get('requests_made')
            if disp_req > 0:
                if disp_req < qtd_of_requests:
                    logger.debug(f'Token gotten! {token, disp_req}')
                    return {key: token}, disp_req
                logger.debug(f'Token gotten! {token, qtd_of_requests}')
                return {key: token}, qtd_of_requests
            if diff_in_hours(now, token.get('last_use')) < 1:
                token['requests_made'] = 0
                logger.debug(f'Token gotten! {token, MAX_REQUESTS_TO_GITHUB}')
                return {key: token}, qtd_of_requests

def update_token_use(token_data: dict[str, TokenInfo], qtd_of_request_made: int):
    key = list(token_data.keys())[0]
    token = token_data.get(key)
    token['last_use'] = datetime.now()
    token['requests_made'] += qtd_of_request_made
    TOKENS.update(token_data)

def map_prs_response(responses: list[dict]):
    prs, errors = [], []
    logger.debug('Mapping responses')
    for response in responses:
        data = safe_get_value(response, ('data',), default_value={})
        if not data:
            errors.append(response)
            data = {}
        for value in data.get('repository', {}).get('pullRequests', {}).get('nodes', []):
            prs.append(Pr(
                created_at=value.get('createdAt'),
                merged_at=value.get('mergedAt'),
                closed_at=value.get('closedAt'),
                deletion_count=value.get('deletions'),
                additions_count=value.get('additions'),
                body=base64.encodebytes(value.get('body', '').encode()).decode(),
                comment_count=value.get('comments').get('totalCount'),
                participants_count=value.get('participants').get('totalCount')
            ))
    logger.debug(f'Mapped {len(prs)}')
    return prs, errors

def persist_errors(repository: Repository, queries: list[str], error: Exception):
    dir_key = f'{repository.get("owner")}_{repository.get("name")}'
    logger.debug(f'Persisting errors to {dir_key}')
    base_path = Path(f'{BASE_PERSISTANCE_PATH}/{dir_key}/')
    if not base_path.exists():
        os.mkdir(base_path)    
    base_path = base_path.joinpath('ERROR/')
    if not base_path.exists():
        os.mkdir(base_path)
    now = datetime.now().isoformat()
    formatted_problem = {
        'repository': repository,
        'error': str(error),
        'queries': queries
    }
    base_path = base_path.joinpath(f'{now}.json')
    with open(base_path,  'w+') as f:
        f.write(json.dumps(formatted_problem, indent=3))

def persist_prs_responses(repository: Repository, prs: list[Pr]):
    def pr_to_csv(pr: Pr):
        # ('created_at','merged_at','closed_at','deletion_count','additions_count','body','comment_count','participants_count')
        return (pr.get('created_at'), pr.get('merged_at'), pr.get('closed_at'), pr.get('deletion_count'), pr.get('additions_count'), pr.get('body'), pr.get('comment_count'), pr.get('participants_count'))
    dir_key = f'{repository.get("owner")}_{repository.get("name")}'
    base_path = Path(f'{BASE_PERSISTANCE_PATH}/{dir_key}/')
    if not base_path.exists():
        os.mkdir(base_path)    
    base_path = base_path.joinpath('OK/')
    if not base_path.exists():
        os.mkdir(base_path)
    persistance_file_path = base_path.joinpath('prs.csv')
    formatted_prs = []
    open_file_mode = 'w' 
    if not persistance_file_path.exists():
        open_file_mode = 'w+'
        formatted_prs = [PR_CSV_COLUMNS]
        formatted_prs.extend([pr_to_csv(pr) for pr in prs])
    with open(persistance_file_path, open_file_mode) as f:
        csv_writer = csv.writer(f)
        if not formatted_prs:
            formatted_prs = [pr_to_csv(pr) for pr in prs]
        csv_writer.writerows(formatted_prs)
            

async def execute_queries(repo_query: list[tuple[Repository, list[str]]]):
    class_manager = ClassContainer()
    q3_service = class_manager.get_question_3_service()
    ordered_repo_query = order_repos_queries_exec_by_qtd(repo_query)
    async def execute(repository: Repository, queries: list[str]):
        exceed_queries = []
        for query_chunk in chunk_list(queries, QUERIES_CHUNK_SIZE):
            try:
                # logger.debug(f'Will execute {query_chunk}')
                query_chunk_size = len(query_chunk)
                token, qtf_of_possible_requests = get_disponible_token(query_chunk_size)
                if query_chunk_size > qtf_of_possible_requests:
                    logger.debug(f'The token can only make {qtf_of_possible_requests}')
                    query_chunk, exceed = partiiton_list(query_chunk, qtf_of_possible_requests - 1)
                    exceed_queries.extend(exceed)
                response = await q3_service.execute_queries(list(token.values())[0].get('token'), query_chunk)
                update_token_use(token, qtf_of_possible_requests)
                prs, errors = map_prs_response(response)
                persist_prs_responses(repository, prs)
                if errors:
                    persist_errors(repository, query_chunk, SomethingException(errors))
                logger.debug('Will sleep for 30secs to cooldown...')
                sleep(30)
                logger.debug('Slept...Moving on')
            except Exception as e:
                logger.error('Error occurred to make requests to repo', exc_info=True)
                persist_errors(repository, query_chunk, e)
        return exceed_queries
    for repository, queries in ordered_repo_query:
        name_owner = f"{repository.get('owner')}_{repository.get('name')}"
        if name_owner in BLACKLIST_REPOS:
            logger.debug(f'Repo {name_owner} in BLACKLIST')
            continue
        logger.debug(f'Making requests to repository {name_owner}')
        all_queries_made = False
        while not all_queries_made:
            exceed_queries = await execute(repository, queries)
            all_queries_made = len(exceed_queries) == 0
            queries = exceed_queries


async def execute():
    class_manager = ClassContainer()
    q3_service = class_manager.get_question_3_service()
    repositories = await q3_service.get_famous_repositories()
    all_possible_queries_per_repo = mount_every_possible_query_for_repositories(repositories)
    await execute_queries(all_possible_queries_per_repo)
    

asyncio.run(execute())

