from os import system

def clone(url) :
    system(f'git clone {url}')