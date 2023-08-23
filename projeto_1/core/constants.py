import os

BASE_GRAPTHQL_PATH = 'https://api.github.com/graphql'

# PERSONAL GITHUB_TOKEN
GITHUB_AUTH_TOKEN = os.getenv('GITHUB_AUTH_TOKEN', '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')

DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH = int(os.getenv('DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH', '50'))
TOTAL_QUANTITY_OF_REPOSITORIES = int(os.getenv('DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH', '1_000'))

# 1 == True | 0 == False
# BE AWARED THIS MAY SLOW DOWN THE PEFORMANCE...
PERSIT_GRAPQHL_QUERIES = bool(os.getenv('PERSIT_GRAPQHL_QUERIES', '1'))
