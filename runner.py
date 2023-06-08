if __name__ == '__main__':
    import bspc.query
    # from bspc.classes import Node, rectangle_type

    nodes = bspc.query.nodes( desktop_selector='focused')

    for node in nodes:
        print(node.name)






