# import asyncio
# from lch.core.clients.graphql_client import GraphqlClient
# from lch.modules.Q2.q2_service import Q2Service
# from lch.modules.analysers.repository_analyser import RepositoryAnalyser
# from lch.modules.auth.service.auth_service import AuthService
# from lch.modules.data_persitance.data_persistance_repository import DataPersistanceRepository
# from lch.modules.file.service.file_service import FileService
# from lch.modules.github.github_service import GithubService

# gq_cli = GraphqlClient()
# fc_service = FileService()
# auth_service = AuthService(file_service=fc_service)
# gh_repo = GithubService(
#     graphql_client=gq_cli,
#     auth_service=auth_service
# )
# repo_ana = RepositoryAnalyser()
# data_repo = DataPersistanceRepository()
# q2_service = Q2Service(
#     github_repository=gh_repo,
#     repository_analyser=repo_ana,
#     data_persitance_service=data_repo
# )

# asyncio.run(q2_service.execute())

import csv
from pathlib import Path

from lch.modules.graphic.graphic_service import GraphicService 

repositories_path = 'resources/Q2/final_result.csv'
correct_repos_path = 'resources/Q2/corrected_final_result.csv'

def fix_repos():
    with open(repositories_path) as f:
        corrected_rows = []
        rows = csv.reader(f)
        for row in rows:
            is_valid_row = True
            for value in row:
                if not value:
                    is_valid_row = False
                    break
            if is_valid_row:
                corrected_rows.append(row)

    with open(correct_repos_path, 'w+') as f:
        csv_writter = csv.writer(f)
        csv_writter.writerows(corrected_rows)

def get_rq_data(row, rq: int):
    main_data = 0
    loc = float(row[4])
    dit = float(row[5])
    cbo = float(row[6])
    lcom =float(row[7])
    if rq == 1:
        main_data = float(row[2])
    elif rq == 2:
        main_data = float(row[3])
    elif rq == 3:
        main_data = float(row[1])
    else:
        main_data = loc
    return [main_data, loc], [main_data, dit], [main_data, cbo], [main_data, lcom]

def fill_data(bucket, data, rq):
    bucket_data = bucket.get(rq)
    bucket_data['dit'].append(data[1])
    bucket_data['cbo'].append(data[2])
    bucket_data['lcom'].append(data[3])

def generate_graphs():
    gphs = GraphicService()
    base_path = 'resources/RQ'

    data = {
        1: {'dit': [], 'cbo': [], 'lcom': []},
        2: {'dit': [], 'cbo': [], 'lcom': []},
        3: {'dit': [], 'cbo': [], 'lcom': []},
        4: {'dit': [], 'cbo': [], 'lcom': []},
    }

    with open(correct_repos_path) as f:
        rows = csv.reader(f)
        next(rows)
        for row in rows:
            d_1 = get_rq_data(row, 1)
            fill_data(data, d_1, 1)

            d_2 = get_rq_data(row, 2)
            fill_data(data, d_2, 2)

            d_3 = get_rq_data(row, 3)
            fill_data(data, d_3, 3)

            d_4 = get_rq_data(row, 4)
            fill_data(data, d_4, 4)


    rq_name = ['stars', 'age', 'release', 'tamanho']
    keys = ('dit', 'cbo', 'lcom')
    rqs = []
    for _ in range(4):
        k = []
        for i, key in enumerate(keys):
            k.append([rq_name[_], key])
        rqs.append(k)

    for i,rq in enumerate(rqs):
        i +=1
        path = f'{base_path}/{i}'
        for rq_p in rq:
            p = Path(f'{path}/{rq_p[1]}')
            gphs.create_scatter_plot(
                file_path=p,
                columns=rq_p,
                data=data.get(i).get(rq_p[1])
            )
        print('')

# fix_repos()
generate_graphs()
