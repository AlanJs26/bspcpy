import re
import bspc.query
from bspc.classes import Node

behaviour = 'swap'
s_string = r'julia'

def match_name(node: Node):
    return bool(re.search(s_string, node.name, flags=re.I))

hidden_nodes = bspc.query.nodes('.hidden')
floating_nodes = bspc.query.nodes('.floating').sort(lambda x:x.id)

matched = floating_nodes.filter(match_name)

matched_visible = matched - hidden_nodes 
matched_hidden = hidden_nodes & matched 
matched_marked = bspc.query.nodes('.floating.marked') & matched 

matched_focused = (bspc.query.nodes('.focused') & matched_visible).pop() 

if behaviour in ['i3', 'swap']:
    if matched_visible:
        next_node = matched_hidden.next(matched_focused)
        for node in matched_visible:
            node.hidden = True
            if next_node:
                node.marked = False

        if next_node:
            next_node.marked = True
            if behaviour == 'swap':
                next_node.hidden = False
                next_node.to_monitor('focused', follow=True)
                next_node.focus()
        exit()
elif behaviour == 'nomark':
    if matched_visible:
        for node in matched_visible:
            node.hidden = True

        current_node = matched_hidden.next(matched_focused)
    else:
        current_node = matched_hidden.first()

    if current_node:
        current_node.hidden = False
        current_node.to_monitor('focused', follow=True)
        current_node.focus()

    exit()

matched_marked_hidden = matched_marked & matched_hidden

if matched_marked_hidden:
    current_node = matched_marked_hidden.first()
else:
    current_node = matched_hidden.first()

if current_node:
    current_node.hidden = False
    current_node.to_monitor('focused', follow=True)
    current_node.focus()




