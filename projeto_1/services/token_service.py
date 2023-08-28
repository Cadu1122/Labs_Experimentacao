token = ''

def search_token():
    with open('resources/core/token', 'r') as token_file:
        return token_file.read()
    
def get_token():
    global token

    if token == '':
        token = search_token()
    return token