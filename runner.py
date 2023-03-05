if __name__ == '__main__':
    import bspc.query
    from bspc.classes import Node, rectangle_type
    from Xlib import display
    from sys import argv
    import zmq
    from time import sleep
    from threading import Event, Thread
    from rich import print
    from typing import Literal

    if len(argv) <= 1:
        print('insuficient arguments')
        exit()

    context = zmq.Context()

    if argv[1] != '--daemon':
        if argv[1] not in ['hold', 'release']:
            print('unknown command')
        else:
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://127.0.0.1:41491")

            socket.send(argv[1].encode('utf-8'))

            socket.close()
            context.term()
        exit()

    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:41491')

    def check_rect(x:int, y:int, rectangle:dict[str,int]):
        if (x >= rectangle['x'] and x <= rectangle['x']+rectangle['width'] and
            y >= rectangle['y'] and y <= rectangle['y']+rectangle['height']):
            return True
        return False

    def find_node_below(obj, x:int, y:int, float_node_id:int):
        match obj:
            case {
                'id': id,
                'client': {
                    'tiledRectangle': rectangle
                }
            } if id != float_node_id and check_rect(x,y,rectangle):
                return id
            case {
                'firstChild': firstChild,
                'secondChild': secondChild
            }:
                a = find_node_below(firstChild, x, y, float_node_id)
                b = find_node_below(secondChild, x, y, float_node_id)
                return a or b
            case _:
                return None

    def rect_center(rectangle:dict[str,int]|rectangle_type):
        return {
            'x': int(rectangle['x']+rectangle['width']/2),
            'y': int(rectangle['y']+rectangle['height']/2)
        }


    def hold_window(event, node:Node, hold_behaviour: Literal['tiled', 'floating']):
        screen = display.Display().screen().root
        pointer = screen.query_pointer()
        x = pointer.root_x
        y = pointer.root_y

        if node.client and hold_behaviour == 'tiled':
            rectangle = node.client['floatingRectangle']
            node.resize(
                'bottom_right',
                node.client['tiledRectangle']['width']-rectangle['width'],
                node.client['tiledRectangle']['height']-rectangle['height']
            )
            node = Node(node.id) or node
            if node.client:
                rectangle = node.client['floatingRectangle']
                center = rect_center(rectangle)
                node.move(x-center['x'], y-center['y'])
        while True:
            if event.is_set():
                event.clear()
                break
            pointer = screen.query_pointer()
            if pointer.root_x == x and pointer.root_y == y:
                continue

            node.move(pointer.root_x-x, pointer.root_y-y)
            x = pointer.root_x
            y = pointer.root_y
            sleep(0.05)

    is_holding = False

    event = Event()
    focused_node: Node|None = None
    hold_behaviour: Literal['tiled','floating'] = 'tiled'
    while True:
        message = socket.recv().decode('utf-8')
        socket.send(b'pong')

        print(message)

        if message == 'hold':
            if is_holding:
                print('already holding window')
            else:
                focused_node = bspc.query.nodes('focused').pop()
                if focused_node:
                    if  focused_node.layout in ['tiled', 'pseudo_tiled']:
                        focused_node.layout = 'floating'
                        hold_behaviour = 'tiled'
                    else:
                        hold_behaviour = 'floating'

                    thread = Thread(target=hold_window, args=(event, focused_node, hold_behaviour))
                    thread.start()
                    is_holding = True
                else:
                    print('there is any windows on focus')
        elif message == 'release':
            event.set()
            if is_holding and focused_node and hold_behaviour == 'tiled':
                pointer = display.Display().screen().root.query_pointer()
                mouse_x = pointer.root_x
                mouse_y = pointer.root_y

                desktop = bspc.query.desktops('focused').pop()

                node_id = find_node_below(desktop.root, mouse_x, mouse_y, focused_node.id)
                if node_id:
                    node_below = Node(node_id)
                    if node_below.client:
                        center = rect_center(node_below.client['tiledRectangle'])
                        center['x'] = center['x']-mouse_x 
                        center['y'] = center['y']-mouse_y 

                        direction=None
                        if abs(center['x']) > abs(center['y']):
                            if center['x'] >= 0:
                                direction='west'
                            else:
                                direction='east'
                        else:
                            if center['y'] >= 0:
                                direction='north'
                            else:
                                direction='south'

                        print(direction)
                        node_below.presel_dir(direction)
                    focused_node.to_node(node_below.id)
                focused_node.layout = 'tiled'
            is_holding = False




