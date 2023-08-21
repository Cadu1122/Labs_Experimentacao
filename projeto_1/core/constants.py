import os

BASE_GRAPTHQL_PATH = 'https://api.github.com/graphql'

# PERSONAL GITHUB_TOKEN
GITHUB_AUTH_TOKEN = os.getenv('GITHUB_AUTH_TOKEN', '')

DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH = int(os.getenv('DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH', '50'))
