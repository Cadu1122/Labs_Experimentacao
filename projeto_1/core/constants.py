import os

BASE_GRAPTHQL_PATH = 'https://api.github.com/graphql'

DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH = int(os.getenv('DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH', '50'))
TOTAL_QUANTITY_OF_REPOSITORIES = int(os.getenv('TOTAL_QUANTITY_OF_REPOSITORIES', '1_000'))

# 1 == True | 0 == False
# BE AWARED THIS MAY SLOW DOWN THE PEFORMANCE...
PERSIT_GRAPQHL_QUERIES = bool(os.getenv('PERSIT_GRAPQHL_QUERIES', '0'))
PREFER_GET_PERSISTED_DATA_OVER_FETCH = bool(os.getenv('PERSIT_GRAPQHL_QUERIES', '0'))


MOST_FAMOUS_LANGUAGES = set(['Javascript', 'Python', 'Java', 'Typescript', 'C#', 'C++', 'PHP', 'Shell', 'C', 'Ruby'])
DEBUG_PATH = 'resources/debug/'
REPOSITORIES_PATH = 'resources/repositories.csv'
GRAPHIC_PATH = 'resources/graphic/'