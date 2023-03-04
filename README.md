# bspcpy

> It's a wrapper for the bspwm command line utility `bspc`.

bspwm is an awesome tiling window manager with a bunch of features, but when I need to develop some script that is a bit more advanced, there are not many options other than using a bash script ~~(which I hate)~~. So, to address this problem, I wrote this simple API.

## Usage

Since everything has the same names as the original bspc, It should be very easy to use.

For now, I have only implemented the query commands

```python
nodes(selector: str) -> Node_set()
desktops(selector: str) -> set[Desktop]
monitors(selector: str) -> set[Monitor]
```

and the classes that represent nodes, desktops, and monitors.

All query methods return Python sets, so it is possible to filter the nodes using set notation.

```python
from bspc import query

floating_nodes = query.nodes('.floating')

for node in floating_nodes:
    if 'firefox' in node.name: 
        node.layout = 'tiled'
```

> This snippet finds all floating Firefox windows and puts them in tiled layout.

I wrote an implementation of a scratchpad using bspcpy in the `examples` folder.

## Requirements

- [xwininfo](https://archlinux.org/packages/extra/x86_64/xorg-xwininfo/)

## Installation

### Via pip

```bash
python -m pip install bspcpy
```

### Upgrade 

```bash
python -m pip install --upgrade bspcpy
```
