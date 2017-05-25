import socket
import sys
from io import StringIO
import copy

socket_ip = "localhost"
socket_port = 60000
Clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    Clientsocket.connect((socket_ip, socket_port))
    messg = Clientsocket.makefile('r')
except:
    print('Server not online')
    sys.exit()


class Agent:
    def __init__(self):
        self.x = 0
        self.y = 0
        # self.rule = {('S', 'l'): 'E', ('S', 'r'): 'W',
        #              ('E', 'l'): 'N', ('E', 'r'): 'S',
        #              ('N', 'l'): 'W', ('N', 'r'): 'E',
        #              ('W', 'l'): 'S', ('W', 'r'): 'N'}
        # direction: E:0 S:1 W:2 N:3
        # self.direction = "S"
        self.direction = 1
        self.map = Map()
        self.have_key = False
        self.have_axe = False
        self.have_boat = False
        self.have_dynamite = 0
        self.item = {'u': '-', 'c': 'T', 'b': ('*', 'T')}
        self.path_find_visited = set()
        self.dynamite_locations = set()
        self.axe_locations = set()
        self.key_locations = set()
        self.door_locations = set()
        self.tree_locations = set()
        self.wall_locations = set()
        self.random_walk = True

    def random_explore(self):
        pass

    def make_decision(self):
        if self.random_walk:
            self.random_explore()
        if self.dynamite_locations:
            for loc in self.dynamite_locations:
                path = self.path_find(loc)
                if path:
                    return self.path_to_output(path)
        if (not self.have_key) and self.key_locations:
            for loc in self.key_locations:
                path = self.path_find(loc)
                if path:
                    return self.path_to_output(path)
        if (not self.have_axe) and self.axe_locations:
            for loc in self.axe_locations:
                path = self.path_find(loc)
                if path:
                    return self.path_to_output(path)

    def get_neighbours(self, current):
        x, y = current
        neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        available_neighbours = []
        for move in neighbours:
            if move in self.map.map_dict and move not in self.path_find_visited and self.map.map_dict[move] == ' ':
                available_neighbours.append(move)
        return available_neighbours

    def get_cost(self, current, target):
        return abs(current[0] - target[0]) + abs(current[1] - target[1])

    def path_find(self, target):
        current = self.x, self.y
        next_move = self.get_neighbours(current)
        if current==target:
            return [current]
        if target in next_move:
            self.path_find_visited.add(target)
            return [current, target]
        path_list = []
        cost_list = []
        for move in next_move:
            cost_list.append((self.get_cost(move, target), move))
        cost_list.sort()
        find_flag = 0
        for cost, move in cost_list:
            self.path_find_visited.add(move)
            path_list = self._path_find(move, target)
            if path_list:
                find_flag = 1
                break
        # reset temporary dict
        self.path_find_visited = set()
        if find_flag:
            return [current] + path_list
        else:
            return

    def _path_find(self, current, target):
        next_move = self.get_neighbours(current)
        path_list = []
        if target in next_move:
            self.path_find_visited.add(target)
            return [current, target]
        cost_list = []
        for move in next_move:
            cost_list.append((self.get_cost(move, target), move))
        cost_list.sort()
        find_flag = 0
        for cost, move in cost_list:
            self.path_find_visited.add(move)
            path_list = self._path_find(move, target)
            if path_list:
                find_flag = 1
                break
        if find_flag:
            return [current] + path_list
        else:
            return

    def path_to_output(self, path):
        x_n, y_n = path[1]
        x_d = x_n - self.x
        y_d = y_n - self.y
        if x_d == -1 and y_d == 0:
            direction = 2
        elif x_d == 1 and y_d == 0:
            direction = 0
        elif x_d == 0 and y_d == 1:
            direction = 3
        elif x_d == 0 and y_d == -1:
            direction = 1
        if self.direction == direction:
            return 'f'
        else:
            d_d = (direction - self.direction) % 4
            if d_d <= 2:
                return 'r'
            else:
                return 'l'



    def get_direction(self, direction, action):
        if action == 'l':
            return (direction - 1) % 4
        else:
            return (direction + 1) % 4
            # return self.rule[(self.direction, action)]

    def use_item(self, action):
        if self.direction == 1:
            if self.map.map_dict[(self.x - 1, self.y)] not in self.item[action]:
                return
            self.map.map_dict[(self.x - 1, self.y)] = ' '
        if self.direction == 3:
            if self.map.map_dict[(self.x + 1, self.y)] not in self.item[action]:
                return
            self.map.map_dict[(self.x + 1, self.y)] = ' '
        if self.direction == 0:
            if self.map.map_dict[(self.x, self.y + 1)] not in self.item[action]:
                return
            self.map.map_dict[(self.x, self.y + 1)] = ' '
        if self.direction == 2:
            if self.map.map_dict[(self.x, self.y - 1)] not in self.item[action]:
                return
            self.map.map_dict[(self.x, self.y - 1)] = ' '

    def update_map(self, window, action):
        print(self.direction)
        if len(self.map.map_dict) == 0:
            self.map.map_dict = copy.deepcopy(window)
            self.map.map_dict[(0, 0)] = 's'
            self.map.South_board = -2
            self.map.North_board = 2
            self.map.East_board = 2
            self.map.West_board = -2
        else:
            if action == 'l' or action == 'r':
                self.direction = self.get_direction(self.direction, action)
                # print(self.direction)
            elif action == 'f':
                if self.direction == 1:
                    self.x -= 1
                    self.map.South_board -= 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or self.map.map_dict[(self.x, self.y)] == '-':
                        self.x += 1
                        return
                    for i in range(-2, 3):
                        loc=(self.x - 2, self.y + i)
                        self.map.map_dict[loc] = window[(-2, i)]
                        if window[(-2, i)] == 'k':
                            self.key_locations.add(loc)
                        elif window[(-2, i)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(-2, i)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(-2, i)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(-2, i)] == '*':
                            self.wall_locations.add(loc)
                if self.direction == 3:
                    self.x += 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.x -= 1
                        return
                    self.map.North_board += 1
                    for i in range(-2, 3):
                        loc = (self.x + 2, self.y - i)
                        self.map.map_dict[loc] = window[(-2, i)]
                        if window[(-2, i)] == 'k':
                            self.key_locations.add(loc)
                        elif window[(-2, i)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(-2, i)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(-2, i)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(-2, i)] == '*':
                            self.wall_locations.add(loc)
                if self.direction == 0:
                    self.y += 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.y -= 1
                        return
                    self.map.East_board += 1
                    for i in range(-2, 3):
                        loc = (self.x + i, self.y + 2)
                        self.map.map_dict[loc] = window[(-2, i)]
                        if window[(-2, i)] == 'k':
                            self.key_locations.add(loc)
                        elif window[(-2, i)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(-2, i)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(-2, i)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(-2, i)] == '*':
                            self.wall_locations.add(loc)
                if self.direction == 2:
                    self.y -= 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.y += 1
                        return
                    self.map.West_board -= 1
                    for i in range(-2, 3):
                        loc = (self.x - i, self.y - 2)
                        self.map.map_dict[loc] = window[(-2, i)]
                        if window[(-2, i)] == 'k':
                            self.key_locations.add(loc)
                        elif window[(-2, i)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(-2, i)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(-2, i)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(-2, i)] == '*':
                            self.wall_locations.add(loc)
            else:
                self.use_item(action)


class Map:
    def __init__(self):
        self.South_board = 0
        self.North_board = 0
        self.East_board = 0
        self.West_board = 0
        self.map_dict = {}

    def print_map(self):
        L = []
        for i in self.map_dict:
            L.append(i)
        L.sort()
        for x in range(self.North_board, self.South_board - 1, -1):
            for y in range(self.West_board, self.East_board + 1):
                if (x, y) in self.map_dict:
                    # print((x,y), end = '')
                    print(self.map_dict[(x, y)], end='')
                else:
                    print('!', end='')
            print()


window = {}
action = None
robot = Agent()
while True:
    for x in range(-2, 3):
        for y in range(2, -3, -1):
            if not (x == 0 and y == 0):
                ch = messg.read(1)
                if not ch:
                    print('Game Over')
                    sys.exit()
                window[(x, y)] = ch
    # print(window)
    robot.update_map(window, action)
    robot.map.print_map()
    print(robot.path_find((-2, -2)))
    # M.print_map()
    action = input('action:')
    Clientsocket.send(action.encode())
