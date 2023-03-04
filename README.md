# bspcpy

> It's a wrapper for the bspwm command line utility `bspc`.

bspwm is a awesome tiling window manager with a bunch of features, but when I need to develop some script a bit more advanced there is no many options rather than using bash script ~~(that I hate)~~. So to address this problem I wrote this simple api.

## Usage

Is very easy to use, almost everything have the same names as the original bspc.

Meanwhile I have only implemented the query commands

```python
nodes(selector: str) -> Node_set()
desktops(selector: str) -> set[Desktop]
monitors(selector: str) -> set[Monitor]
```
and some classes that represents nodes, desktops and monitors.

all query methods returns python sets, so is possible to filter the nodes using set notation.

```python
from bspc import query

floating_nodes = query.nodes('.floating')

for node in floating_nodes:
    if 'firefox' in node.name: 
        node.layout = 'tiled'
```

> This snippet find all floating firefox windows and put them in tiled layout

An example of a implementation of a scratchpad using bspcpy is located on the `examples` folder

## Requirements

- [xwininfo](https://archlinux.org/packages/extra/x86_64/xorg-xwininfo/)

## Instalation

### Via pip

```bash
python -m pip install bspcpy
```

### Upgrade 

```bash
python -m pip install --upgrade bspcpy
```
