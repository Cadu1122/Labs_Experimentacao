import requests

headers = {"Authorization": "Bearer KEY"}

def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
     
query = """
{
  search(query: "stars:>1", type: REPOSITORY, first: 1000) {
    nodes {
      ... on Repository {
        id
        name
        issues(filterBy: {states: CLOSED}) {
          totalCount
        }
        createdAt
        pullRequests(states: MERGED) {
          totalCount
        }
        releases {
          totalCount
        }
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""