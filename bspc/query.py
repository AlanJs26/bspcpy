import subprocess
from typing import Optional
from .classes import Node, Desktop, Monitor, Node_set, Desktop_set, Monitor_set

def nodes(node_selector:Optional[str]=None, desktop_selector:Optional[str]=None, monitor_selector:Optional[str]=None):
    if not (node_selector or desktop_selector or monitor_selector):
        return Node_set(())
    selector = ''
    if node_selector:
        selector+= f' -n {node_selector}'
    if desktop_selector:
        selector+= f' -d {desktop_selector}'
    if monitor_selector:
        selector+= f' -m {monitor_selector}'

    result = subprocess.run(['bspc', 'query','-N', *selector.split()], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return Node_set(Node(id=int(id, base=16)) for id in ids)


def desktops(desktop_selector:Optional[str]=None, node_selector:Optional[str]=None, monitor_selector:Optional[str]=None):
    if not (node_selector or desktop_selector or monitor_selector):
        return Desktop_set(())
    selector = ''
    if node_selector:
        selector+= f' -n {node_selector}'
    if desktop_selector:
        selector+= f' -d {desktop_selector}'
    if monitor_selector:
        selector+= f' -m {monitor_selector}'

    result = subprocess.run(['bspc', 'query','-D', *selector.split()], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return Desktop_set(Desktop(id=int(id, base=16)) for id in ids)


def monitors(monitor_selector:Optional[str]=None, node_selector:Optional[str]=None, desktop_selector:Optional[str]=None):
    if not (node_selector or desktop_selector or monitor_selector):
        return Monitor_set(())
    selector = ''
    if node_selector:
        selector+= f' -n {node_selector}'
    if desktop_selector:
        selector+= f' -d {desktop_selector}'
    if monitor_selector:
        selector+= f' -m {monitor_selector}'

    result = subprocess.run(['bspc', 'query','-M', *selector.split()], capture_output=True, text=True)

    ids = result.stdout.splitlines()

    return Monitor_set(Monitor(id=int(id, base=16)) for id in ids)

