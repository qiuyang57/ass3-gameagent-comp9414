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

class Map:
    def __init__(self):
        self.direction = 'S'
        self.South_board = 0
        self.North_board = 0
        self.East_board = 0
        self.West_board = 0
        self.map = {}
        self.x = 0
        self.y = 0
    def get_direction(self,direction,action):
        self.rule = {('S','l'):'E',('S','r'):'W',
                     ('E','l'):'N',('E','r'):'S',
                     ('N','l'):'W',('N','r'):'E',
                     ('W','l'):'S',('W','r'):'N'}
        return self.rule[(direction,action)]
    def update_map(self,window,action):
        if len(self.map) == 0:
            self.map = copy.deepcopy(window)
            self.map[(0,0)] = 'start'
            self.South_board = -2
            self.North_board = 2
            self.East_board = 2
            self.West_board = -2
        else:
            if action == 'l' or action == 'r':
                self.direction = self.get_direction(self.direction,action)
                print(self.direction)
            elif action == 'f':
                if self.direction == 'S':
                    self.y -= 1
                    for i in range(2,-3,-1):
                        self.map[(self.x - i,self.y - 2)] = window[-i,-2]
                if self.direction == 'N':
                    self.y += 1
                    for i in range(2,-3,-1):
                        self.map[(self.x - i,self.y + 2)] = window[-i,2]
                if self.direction == 'E':
                    self.x += 1
                    for i in range(2,-3,-1):
                        self.map[(self.x + 2,self.y - i)] = window[2,-i]
                if self.direction == 'W':
                    self.x -= 1
                    for i in range(2,-3,-1):
                        self.map[(self.x - 2,self.y - i)] = window[-2,-i]
    def print_map(self):
        L = []
        for i in self.map:
            L.append(i)
        L.sort()
        for i in L:
            print(self.map[i])

window ={}
action = ''
M = Map()
while True:
    for j in range(-2,3):
        for i in range(2,-3,-1):
            if not (i == 0 and j == 0):
                ch = messg.read(1)
                if not ch:
                    print('Game Over')
                    sys.exit()
                window[(i,j)] = ch
    #print(window)
    action = input('action:')
    M.update_map(window,action)
    M.print_map()
    Clientsocket.send(action.encode())
