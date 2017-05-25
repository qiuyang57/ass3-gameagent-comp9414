import socket
import sys
from io import StringIO
import copy
socket_ip = "localhost"
socket_port = 60000
Clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    Clientsocket.connect((socket_ip,socket_port))
    messg = Clientsocket.makefile('r')
except:
    print('Server not online')
    sys.exit()


class Agent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = 'S'
        self.map = Map()
        self.have_key = False
        self.have_axe = False
        self.have_boat = False
        self.have_dynamite = False

    def get_direction(self, direction,action):
        self.rule = {('S', 'l'): 'E', ('S', 'r'): 'W',
                     ('E', 'l'): 'N', ('E', 'r'): 'S',
                     ('N', 'l'): 'W', ('N', 'r'): 'E',
                     ('W', 'l'): 'S', ('W', 'r'): 'N'}
        return self.rule[(self.direction, action)]

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
                self.direction = self.get_direction(self.direction,action)
                #print(self.direction)
            elif action == 'f':
                if self.direction == 'S':
                    self.x -= 1
                    self.map.South_board -= 1
                    if self.map.map_dict[(self.x ,self.y)] == '*' or self.map.map_dict[(self.x ,self.y)] == 'T' or self.map.map_dict[(self.x ,self.y)] == '-':
                        self.x += 1
                        return
                    for i in range(-2,3):
                        self.map.map_dict[(self.x - 2,self.y + i)] = window[(-2,i)]
                if self.direction == 'N':
                    self.x += 1
                    if self.map.map_dict[(self.x ,self.y)] == '*' or self.map.map_dict[(self.x ,self.y)] == 'T' or self.map.map_dict[(self.x ,self.y)] == '-':
                        self.x -= 1
                        return
                    self.map.North_board += 1
                    for i in range(-2,3):
                        self.map.map_dict[(self.x + 2,self.y - i)] = window[(-2,i)]
                if self.direction == 'E':
                    self.y += 1
                    if self.map.map_dict[(self.x ,self.y)] == '*' or self.map.map_dict[(self.x ,self.y)] == 'T' or self.map.map_dict[(self.x ,self.y)] == '-':
                        self.y -= 1
                        return
                    self.map.East_board += 1
                    for i in range(-2,3):
                        self.map.map_dict[(self.x + i,self.y + 2)] = window[(-2,i)]
                if self.direction == 'W':
                    self.y -= 1
                    if self.map.map_dict[(self.x ,self.y)] == '*' or self.map.map_dict[(self.x ,self.y)] == 'T' or self.map.map_dict[(self.x ,self.y)] == '-':
                        self.y += 1
                        return
                    self.map.West_board -= 1
                    for i in range(-2,3):
                        self.map.map_dict[(self.x - i,self.y - 2)] = window[(-2,i)]

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




window ={}
action = None
robot = Agent()
while True:
    for x in range(-2,3):
        for y in range(2,-3,-1):
            if not (x == 0 and y == 0):
                ch = messg.read(1)
                if not ch:
                    print('Game Over')
                    sys.exit()
                window[(x,y)] = ch
    #print(window)
    robot.update_map(window,action)
    robot.map.print_map()
    #M.print_map()
    action = input('action:')
    Clientsocket.send(action.encode())
