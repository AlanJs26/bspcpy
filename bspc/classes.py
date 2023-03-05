from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
import subprocess
import json
from typing import Iterable, Literal, TypedDict, Callable
from operator import attrgetter
from copy import copy

NODE_FLAGS = ['hidden', 'sticky', 'private', 'locked', 'marked']
WINDOW_STATES = ["tiled","pseudo_tiled","floating","fullscreen"]

class constraints_type(TypedDict):
    min_width:int
    min_height:int

class padding_type(TypedDict):
    top:int
    right:int
    bottom: int
    left: int

class rectangle_type(TypedDict):
    x:int
    y:int
    width: int
    height: int

class client_type(TypedDict):
    className:str
    instanceName:str
    borderWidth:int
    state:str
    lastState:str
    layer:str
    lastLayer:str
    urgent:bool
    shown:bool
    tiledRectangle:rectangle_type
    floatingRectangle:rectangle_type

class node_type(TypedDict):
    id:int
    splitType: str
    splitRatio: float
    vacant: bool
    hidden: bool
    sticky: bool
    private: bool
    locked: bool
    marked: bool
    presel: str
    rectangle: rectangle_type
    constraints: constraints_type
    firstChild: str
    secondChild: str
    client: client_type

class desktop_type(TypedDict):
    id:int
    name:str
    layout:str
    userLayout:str
    windowGap:int
    borderWidth:int
    focusedNodeId:int
    padding:padding_type
    root:node_type

class Node_set():
    def __init__(self, iterator:Iterable['Node'], ordered=False):
        self._set:set[Node] = set(iterator)
        self.ordered = ordered

    def pop(self) -> 'Node|None':
        if not len(self._set):
            return None
        return max(self._set, key=attrgetter('index'))
    def first(self) -> 'Node|None':
        if not len(self._set):
            return None
        return min(self._set, key=attrgetter('index'))

    def next(self, node:'Node|None') -> 'Node|None':
        if not node:
            return None

        next_node = next((item for item in sorted(self._set, key=lambda x:x.index) if item.index > node.index and item != node),None) 

        return next_node or self.first()

    def filter(self, callback:Callable[['Node'], bool]):
        new_set = copy(self._set)
        for item in self._set:
            if not callback(item):
                new_set.remove(item)
        return Node_set(new_set, ordered=self.ordered)
    
    def sort(self, key:Callable[['Node'], SupportsRichComparison], reverse=False):
        self.ordered = True
        for i,node in enumerate(sorted(self._set, key=key, reverse=reverse)):
            node.__dict__['index'] = i
        return self

    def intersection(self, other:'Node_set'):
        return Node_set(self._set.intersection(other), ordered=self.ordered)
    def difference(self, other:'Node_set'):
        return Node_set(self._set.difference(other), ordered=self.ordered)
    def __and__(self, other:'Node_set'):
        return Node_set(self._set.intersection(other), ordered=self.ordered)
    def __sub__(self, other:'Node_set'):
        return Node_set(self._set.difference(other), ordered=self.ordered)
    def __iter__(self):
        return iter(self._set)
    def __repr__(self):
        return repr(self._set)
    def __bool__(self):
        return bool(self._set)

class Node:
    def __init__(self, id:int, index=-1):
        self.index:int
        self.__dict__['index'] = index
        self.id:int
        self.className:str
        self.layout:str

        self.splitType: str
        self.splitRatio: float
        self.vacant: bool
        self.hidden: bool
        self.sticky: bool
        self.private: bool
        self.locked: bool
        self.marked: bool
        self.presel: str
        self.rectangle: rectangle_type
        self.constraints: constraints_type
        self.firstChild: node_type|None
        self.secondChild: node_type|None
        self.client: client_type|None

        result = subprocess.run(['bspc', 'query','-T', '-n', hex(id)], capture_output=True, text=True)

        data = json.loads(result.stdout)
        for item in data:
            self.__dict__[item] = data[item]

        if self.client:
            self.__dict__['className'] = self.client['className']
            self.__dict__['layout'] = self.client['state']
        else:
            self.__dict__['className'] = ''
            self.__dict__['layout'] = ''
        
    def __repr__(self):
        return f'Node(id={hex(self.id)})'

    def __neq__(self, other):
        if not isinstance(other, Node):
            return True
        return self.id != other.id
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __setattr__(self, name, value):
        if name in NODE_FLAGS and isinstance(value, bool):
            self.flag(name, 'on' if value else 'off')
        elif name == 'layout' and value in WINDOW_STATES:
            self.state(value)
        else:
            raise Exception('invalid property')

    @property
    def name(self):
        result = subprocess.run(['xwininfo', '-id', hex(self.id)], check=True, capture_output=True)
        result = subprocess.run(['head', '-n2'], input=result.stdout, check=True, capture_output=True)
        result = subprocess.run(['grep', r'\"(.+)\"', '-E', '-o'], input=result.stdout, check=True, capture_output=True)

        win_name = result.stdout.decode().strip()
        if win_name:
            win_name = win_name[1:-1]

        return win_name

    def command(self, command:str):
        subprocess.run(['bspc', 'node', hex(self.id), *command.strip().split(' ')])

    def balance(self):
        self.command('--balance')

    def equalize(self):
        self.command('--equalize')

    def insert_receptacle(self):
        self.command('--insert-receptacle')

    def kill(self):
        self.command('--kill')

    def close(self):
        self.command('--close')

    def activate(self):
        self.command('-a')

    def focus(self):
        self.command('-f')

    def flag(self, name:Literal['hidden','sticky','private','locked','marked'], state='on'):
        self.command(f'--flag {name}={state}')

    def layer(self, name:Literal['below', 'normal', 'above']):
        self.command(f'--layer {name}')

    def presel_dir(self, direction:Literal['north', 'west', 'south', 'east']):
        self.command(f'--presel-dir {direction}')

    def state(self, name:Literal['tiled', 'pseudo_tiled', 'floating', 'fullscreen']):
        self.command(f'--state {name}')

    def circulate(self, orientation:Literal['forward', 'backward']):
        self.command(f'--circulate {orientation}')

    def flip(self, orientation:Literal['horizontal', 'vertical']):
        self.command(f'--flip {orientation}')

    def rotate(self, angle:Literal[90,270,180]):
        self.command(f'--rotate {angle}')

    def resize(self, handle:Literal['top','left','bottom','right','top_left','top_right','bottom_right','bottom_left'], dx:int, dy:int):
        self.command(f'--resize {handle} {dx} {dy}')

    def move(self, dx:int, dy:int):
        self.command(f'--move {dx} {dy}')

    def swap(self, selector:str|int, follow=False):
        if isinstance(selector,int):
            self.command(f'--swap {hex(selector)} {"--follow" if follow else ""}')
        else:
            self.command(f'--swap {selector} {"--follow" if follow else ""}')

    def to_node(self, selector:str|int, follow=False):
        if isinstance(selector, int):
            self.command(f'--to-node {hex(selector)} {"--follow" if follow else ""}')
        else:
            self.command(f'--to-node {selector} {"--follow" if follow else ""}')

    def to_monitor(self, selector:str|int, follow=False):
        if isinstance(selector,int):
            self.command(f'--to-monitor {hex(selector)} {"--follow" if follow else ""}')
        else:
            self.command(f'--to-monitor {selector} {"--follow" if follow else ""}')

    def to_desktop(self, selector:str|int, follow=False):
        if isinstance(selector,int):
            self.command(f'--to-desktop {hex(selector)} {"--follow" if follow else ""}')
        else:
            self.command(f'--to-desktop {selector} {"--follow" if follow else ""}')


class Desktop:
    def __init__(self, id:int):
        self.id:int

        self.name:str
        self.layout:str
        self.userLayout:str
        self.windowGap:int
        self.borderWidth:int
        self.focusedNodeId:int
        self.padding:padding_type
        self.root:node_type

        result = subprocess.run(['bspc', 'query','-T', '-d', hex(id)], capture_output=True, text=True)

        data = json.loads(result.stdout)
        for item in data:
            self.__dict__[item] = data[item]

    def __setattr__(self):
        raise Exception('invalid property')

    def __eq__(self, other):
        if not isinstance(other, Desktop):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f'Desktop(id={hex(self.id)})'

    def command(self, command:str):
        subprocess.run(['bspc', 'desktop', hex(self.id), *command.split(' ')])

    def activate(self):
        self.command('-a')

    def remove(self):
        self.command('--remove')

    def focus(self):
        self.command('-f')

    def swap(self, selector:str, follow=False):
        self.command(f'--swap {selector} {"--follow" if follow else ""}')

    def to_monitor(self, selector:str|int, follow=False):
        if isinstance(selector,int):
            self.command(f'--to-monitor {hex(selector)} {"--follow" if follow else ""}')
        else:
            self.command(f'--to-monitor {selector} {"--follow" if follow else ""}')

    def rename(self, name:str):
        self.command(f'--rename {name}')

    def bubble(self, name:Literal['forward', 'backward']):
        self.command(f'--bubble {name}')

    def set_layout(self, name:Literal['forward', 'backward', 'monocle', 'tiled']):
        self.command(f'--layout {name}')


class Monitor:
    def __init__(self, id:int):
        self.id:int

        self.name:str
        self.randrId:int
        self.wired:bool
        self.stickyCount:int
        self.windowGap:int
        self.borderWidth:int
        self.focusedDesktopId:int
        self.padding:padding_type
        self.rectangle:rectangle_type
        self.desktops:list[desktop_type]

        result = subprocess.run(['bspc', 'query','-T', '-m', hex(id)], capture_output=True, text=True)

        data = json.loads(result.stdout)
        for item in data:
            self.__dict__[item] = data[item]

    def __setattr__(self):
        raise Exception('invalid property')
        
    def __eq__(self, other):
        if not isinstance(other, Monitor):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f'Monitor(id={hex(self.id)})'

    def command(self, command:str):
        subprocess.run(['bspc', 'monitor', hex(self.id), *command.split(' ')])

    def remove(self):
        self.command('--remove')

    def focus(self):
        self.command('-f')

    def swap(self, selector:str, follow=False):
        self.command(f'--swap {selector} {"--follow" if follow else ""}')

    def reset_desktops(self, name:str):
        self.command(f'--reset-desktops {name}')

    def set_rectangle(self, width:int, height:int, x:int, y:int):
        self.command(f'--rectangle {width}x{height}+{x}+{y}')

    def reorder_desktops(self, name:str):
        self.command(f'--reorder-desktops {name}')

    def add_desktops(self, name:str):
        self.command(f'--add-desktops {name}')

    def rename(self, name:str):
        self.command(f'--rename {name}')

