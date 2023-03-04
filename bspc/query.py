import subprocess
from .classes import Node, Desktop, Monitor, Node_set

def nodes(selector: str):
    result = subprocess.run(['bspc', 'query','-N', '-n', *selector.split(' ')], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return Node_set(Node(id=int(id, base=16)) for id in ids)


def desktops(selector: str):
    result = subprocess.run(['bspc', 'query','-D', '-d', *selector.split(' ')], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return set(Desktop(id=int(id, base=16)) for id in ids)


def monitors(selector: str):
    result = subprocess.run(['bspc', 'query','-M', '-m', *selector.split(' ')], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return set(Monitor(id=int(id, base=16)) for id in ids)

