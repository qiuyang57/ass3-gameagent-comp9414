import socket
import sys
from io import StringIO
import copy
import random

import itertools

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
        self.on_boat = False
        self.sail_allowed= False
        self.have_dynamite = 0
        self.have_gold = False
        self.item = {'u': '-', 'c': 'T', 'b': ('*', 'T')}
        self.path_find_visited = set()
        self.dynamite_locations = set()
        self.axe_locations = set()
        self.key_locations = set()
        self.tree_locations = set()
        self.treasure_location = None
        self.random_walk = True
        self.unvisited_location = set()
        self.cannot_visited_location = set()
        self.visited_location =set()
        self.exploring_target = None
        self.cost_dict = {}
        self.heuristic_dict ={}
        self.parent_dict = {}
        self.sea_locations = set()
        self.visited_sea_location = set()
        self.unvisited_sea_location = set()
        self.exploring_sea_target = None
        self.got_treasure=False
        self.explore_sea=False
        self.cannot_visited_sea = set()
        self.boom_list=set()

    def random_explore_sea(self):
        self.sail_allowed = True
        current_location = self.x, self.y
        self.visited_sea_location.add(current_location)
        self.unvisited_sea_location -= self.visited_sea_location
        if current_location == self.exploring_sea_target:
            self.exploring_sea_target = None
        if not self.exploring_sea_target:
            for loc in self.map.map_dict:
                if loc not in self.sea_locations:
                    self.unvisited_location.add(loc)
                elif loc not in self.visited_sea_location:
                    self.unvisited_sea_location.add(loc)
            while True:
                if not self.unvisited_sea_location:
                    break
                self.exploring_sea_target = sorted(self.unvisited_sea_location, key=lambda sea_node: (
                self.get_cost(current_location, (sea_node[0], sea_node[1]))))[0]
                print(current_location, self.exploring_sea_target)
                # print(self.unvisited_sea_location)
                path = self.path_find(self.exploring_sea_target)
                if path:
                    break
                else:
                    self.cannot_visited_sea.add(self.exploring_sea_target)
                    self.unvisited_sea_location -= self.cannot_visited_sea
            if not self.unvisited_sea_location:
                self.explore_sea= False
                return
            action = self.path_to_output(path)
            return action

        else:
            path = self.path_find(self.exploring_sea_target)
            if not self.unvisited_sea_location:
                self.explore_sea = False
                return
            action = self.path_to_output(path)
            return action

    def random_explore(self):
        current_location = self.x,self.y
        self.visited_location.add(current_location)
        self.unvisited_location -= self.visited_location
        #print(self.unvisited_location)
        #print(self.visited_location)
        #print(current_location,self.exploring_target)
        if current_location == self.exploring_target:
            self.exploring_target = None
        if not self.exploring_target:
            for loc in self.map.map_dict:
                if self.map.map_dict[loc] == '~' and loc not in self.visited_sea_location:
                    self.unvisited_sea_location.add(loc)
                elif loc not in self.visited_location:
                    self.unvisited_location.add(loc)
            while True:
                if not self.unvisited_location:
                    break
                self.exploring_target = sorted(self.unvisited_location, key=lambda node:(self.get_cost(current_location,(node[0],node[1]))))[0]
                # print(current_location,self.exploring_target)
                #self.exploring_target = (random.sample(self.unvisited_location,1))[0]
                path = self.path_find(self.exploring_target)
                if path:
                    break
                else:
                    self.cannot_visited_location.add(self.exploring_target)
                    self.unvisited_location -= self.cannot_visited_location
            if not self.unvisited_location:
                self.random_walk = False
                return
            action = self.path_to_output(path)
            return action
        else:
            path = self.path_find(self.exploring_target)
            if not self.unvisited_location:
                self.random_walk = False
                return
            action = self.path_to_output(path)
            return action

    def make_decision(self):
        if self.random_walk:
            action=self.random_explore()
            if action:
                return action
        if (self.have_boat or self.on_boat) and not self.random_walk:
            self.explore_sea=True
            action = self.random_explore_sea()
            if action:
                return action
        # if self.treasure_location:
        #     self.boom_list=self.dynamite_locations
        #     print(self.path_finding_with_less_bomb())
        if self.got_treasure:
            path = self.path_find((0, 0))
            if path:
                return self.path_to_output(path)
        if self.treasure_location:
            path = self.path_find(self.treasure_location)
            if path:
                # print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
                return self.path_to_output(path)
        if (not self.have_axe) and self.axe_locations:
            # print(self.map.map_dict)
            for loc in self.axe_locations:
                path = self.path_find(loc)
                if path:
                    return self.path_to_output(path)

        if self.treasure_location:
            path = self.path_find(self.treasure_location)
            if path:
                return self.path_to_output(path)
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
        if (not self.have_boat) and self.have_axe:
            for loc in sorted(self.tree_locations,key=lambda loc:self.get_cost((self.x,self.y),loc)):
                path = self.path_find(loc)
                if path:
                    return self.path_to_output(path)
        if not (self.random_walk and self.explore_sea):
            self.random_walk=True
            return self.random_explore()
        print("Error. No decision.")

    def get_neighbours_bomb(self, current):
        x, y = current
        neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        available_neighbours = []
        empty_block_symbols = [' ', 'd', 'k', 'a','$','*']
        if self.have_axe:
            empty_block_symbols += ['T']
        if self.have_key:
            empty_block_symbols += ['-']
        for move in neighbours:
            if move in self.map.map_dict and move not in self.path_find_visited and self.map.map_dict[move] \
                    in empty_block_symbols:
                available_neighbours.append(move)
        return available_neighbours

    def _path_find(self,start,target,previous_bombed_walls,num_bomb_carried,visted_locs):
        current=start
        current_visited_loc=visted_locs.copy()
        current_visited_loc.add(current)
        # self.map.print_map_n(current)
        next_move = self.get_neighbours(current)
        p_bombed_walls = previous_bombed_walls.copy()
        results=[]
        if current==target:
            return [([current],p_bombed_walls,num_bomb_carried)]
        if target in next_move:
            self.path_find_visited.add(target)
            return [([current, target],p_bombed_walls,num_bomb_carried+1)]
        for move in next_move:
            if move not in current_visited_loc:
                if self.map.map_dict[move]=='*' and move not in previous_bombed_walls and num_bomb_carried>=1:
                    # path_list,bombed_walls,num_bomb_left =
                    rs=self._path_find(move,target,p_bombed_walls,num_bomb_carried-1,current_visited_loc)
                    # print(rs)
                    for r in rs:
                        if r:
                            # print(r)
                            a,b,c=r
                            d= b.copy()
                            d.add(move)
                            results.append(([current]+a,d,c-1))
                elif (self.map.map_dict[move]=='*' and move in previous_bombed_walls) or self.map.map_dict[move]!='*':
                    rs=self._path_find(move, target, p_bombed_walls, num_bomb_carried,current_visited_loc)
                    # print(rs)
                    for r in rs:
                        if r:
                            # print(r)
                            a,b,c=r
                            d=b.copy()
                            results.append(([current]+a,d,c))
        # print(results)
        return results

    def wall_cost_a_star(self,start,target,previous_bombed_walls,num_bomb_carried):
        # print(self.random_walk,self.sail_allowed,self.explore_sea,self.on_boat)
        openset = set()
        closedset = set()
        current = start
        # Add the starting point to the open set
        openset.add(current)
        self.cost_dict[current]=(0,0,set())
        self.heuristic_dict[current]=self.get_cost(current,target)
        # While the open set is not empty
        while openset:
            # Find the item in the open set with the lowest G + H score
            priority_list= sorted(openset, key=lambda node: (self.cost_dict[node][0],self.cost_dict[node][1]+self.heuristic_dict[node]))
            current = priority_list[0]
            # print(self.cost_dict)
            # print(priority_list)
            # If it is the item we want, retrace the path and return it
            cost_dynamite = self.cost_dict[current][0]
            wall_bombed = self.cost_dict[current][2]
            if current == target and num_bomb_carried>=cost_dynamite:
                path = []
                while current in self.parent_dict:
                    path.append(current)
                    current = self.parent_dict[current]
                path.append(current)
                self.cost_dict = {}
                self.heuristic_dict = {}
                self.parent_dict = {}
                return path[::-1],num_bomb_carried-cost_dynamite,wall_bombed
            # Remove the item from the open set
            openset.remove(current)
            # Add it to the closed set
            closedset.add(current)
            # Loop through the node's children/siblings
            children = self.get_neighbours_bomb(current)
            for node in children:
                # If it is already in the closed set, skip it
                if node in closedset:
                    continue
                # Otherwise if it is already in the open set
                landscape=self.map.map_dict[node]
                if node in openset:
                    # print(node)
                    # Check if we beat the G score
                    num_dynamites_needed, num_steps,current_bombed_walls = self.cost_dict[current]
                    # print(current_bombed_walls)
                    next_num_dynamites_needed,next_num_steps,next_bombed_walls=self.cost_dict[node]
                    new_bombed_walls = current_bombed_walls.copy()
                    new_bombed_walls.add(node)
                    if landscape == '*' and node not in previous_bombed_walls:
                        new_num_dynamites, new_num_steps = num_dynamites_needed+1, num_steps + 1
                    else:
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + 1
                    if new_num_dynamites<next_num_dynamites_needed:
                        # If so, update the node to have a new parent
                        self.cost_dict[node]=(new_num_dynamites,new_num_steps,new_bombed_walls)
                        self.parent_dict[node]=current
                    elif new_num_dynamites==next_num_dynamites_needed and new_num_steps<next_num_steps:
                        self.cost_dict[node] = (new_num_dynamites, new_num_steps,new_bombed_walls)
                        self.parent_dict[node] = current
                else:
                    num_dynamites_needed, num_steps, current_bombed_walls = self.cost_dict[current]
                    # print(current_bombed_walls)
                    new_bombed_walls = current_bombed_walls.copy()
                    if landscape == '*' and node not in previous_bombed_walls:
                        new_num_dynamites, new_num_steps = num_dynamites_needed+1, num_steps + 1
                        new_bombed_walls.add(node)
                    else:
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + 1
                    # If it isn't in the open set, calculate the G and H score for the node
                    self.cost_dict[node] = (new_num_dynamites, new_num_steps,new_bombed_walls)
                    self.heuristic_dict[node] = self.get_cost(node, target)
                    # Set the parent to our current item
                    self.parent_dict[node] = current
                    # Add it to the set
                    openset.add(node)
        # Throw an exception if there is no path
        self.cost_dict = {}
        self.heuristic_dict ={}
        self.parent_dict = {}
        return None,None,None


    def path_finding_with_less_bomb(self):
        for l in range(0,len(self.boom_list)+1):
            for seq in itertools.permutations(self.boom_list,l):
                seq_n = [(self.x,self.y)]+list(seq)+[self.treasure_location]
                exe_seqs = []
                for i in range(len(seq_n)-1):
                    exe_seqs.append((seq_n[i],seq_n[i+1]))
                total_path=[]
                print(exe_seqs)
                finish=True
                for index,(sta,tar) in enumerate(exe_seqs):
                    print((sta,tar))
                    if index==0:
                        wall_bombed = set()
                        num_bomb_c = self.have_dynamite
                    print(self._path_find(sta,tar,wall_bombed,num_bomb_c,set()))

                #     if path:
                #         num_bomb_c=num_bomb_left+1
                #         total_path+=path
                #     else:
                #         finish = False
                #         break
                # if finish:
                #     return total_path

    def get_neighbours(self, current):
        x, y = current
        neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        available_neighbours = []
        empty_block_symbols = [' ', 'd', 'k', 'a','$']
        if self.have_axe:
            empty_block_symbols += ['T']
        if self.have_key:
            empty_block_symbols += ['-']
        if self.have_boat or self.on_boat:
            empty_block_symbols += ['~']
        if self.have_dynamite:
            empty_block_symbols+=['*']
        for move in neighbours:
            if move in self.map.map_dict and move not in self.path_find_visited and self.map.map_dict[move] \
                    in empty_block_symbols:
                if not (self.map.map_dict[current]=='~' and self.map.map_dict[move] in ['*','T']):
                    available_neighbours.append(move)
        return available_neighbours

    def random_sail_get_neighbours(self, current):
        x, y = current
        neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        available_neighbours = []
        empty_block_symbols = ['~','$']
        for move in neighbours:
            if move in self.map.map_dict and move not in self.path_find_visited and self.map.map_dict[move] \
                    in empty_block_symbols:
                available_neighbours.append(move)
        return available_neighbours

    def random_walk_get_neighbours(self, current):
        x, y = current
        neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        available_neighbours = []
        empty_block_symbols = [' ', 'd', 'k', 'a', '$']
        if self.have_axe:
            empty_block_symbols += ['T']
        if self.have_key:
            empty_block_symbols += ['-']
        for move in neighbours:
            if move in self.map.map_dict and move not in self.path_find_visited and self.map.map_dict[move] \
                    in empty_block_symbols:
                available_neighbours.append(move)
        return available_neighbours

    def get_cost(self, current, target):
        return abs(current[0] - target[0]) + abs(current[1] - target[1])

    def path_find(self, target):
        # print(self.random_walk,self.sail_allowed,self.explore_sea,self.on_boat)
        if self.on_boat:
            land_cost = 1000
            sea_cost = 1
        else:
            land_cost=1
            sea_cost=1
        openset = set()
        closedset = set()
        current = self.x, self.y
        # Add the starting point to the open set
        openset.add(current)
        self.cost_dict[current]=(0,0)
        self.heuristic_dict[current]=self.get_cost(current,target)
        # While the open set is not empty
        while openset:
            # Find the item in the open set with the lowest G + H score
            current = sorted(openset, key=lambda node: (self.cost_dict[node][0],self.cost_dict[node][1]+self.heuristic_dict[node]))[0]
            # If it is the item we want, retrace the path and return it
            if current == target and self.have_dynamite>=self.cost_dict[current][0]:
                path = []
                while current in self.parent_dict:
                    path.append(current)
                    current = self.parent_dict[current]
                path.append(current)
                self.cost_dict = {}
                self.heuristic_dict = {}
                self.parent_dict = {}
                return path[::-1]
            # Remove the item from the open set
            openset.remove(current)
            # Add it to the closed set
            closedset.add(current)
            # Loop through the node's children/siblings
            if self.random_walk:
                children = self.random_walk_get_neighbours(current)
            elif self.sail_allowed and self.explore_sea and not self.on_boat:
                children = self.get_neighbours(current)
            elif self.sail_allowed and self.explore_sea and self.on_boat:
                children = self.random_sail_get_neighbours(current)
            else:
                children = self.get_neighbours(current)
            for node in children:
                # If it is already in the closed set, skip it
                if node in closedset:
                    continue
                # Otherwise if it is already in the open set
                if node in openset:
                    # Check if we beat the G score
                    num_dynamites_needed, num_steps = self.cost_dict[current]
                    next_num_dynamites_needed,next_num_steps=self.cost_dict[node]
                    if self.map.map_dict[node] == '*':
                        new_num_dynamites, new_num_steps = num_dynamites_needed+1, num_steps + land_cost
                    elif self.map.map_dict[node] == '~':
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + sea_cost
                    else:
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + land_cost
                    if new_num_dynamites<next_num_dynamites_needed:
                        # If so, update the node to have a new parent
                        self.cost_dict[node]=(new_num_dynamites,new_num_steps)
                        self.parent_dict[node]=current
                    elif new_num_dynamites==next_num_dynamites_needed and new_num_steps<next_num_steps:
                        self.cost_dict[node] = (new_num_dynamites, new_num_steps)
                        self.parent_dict[node] = current
                else:
                    num_dynamites_needed, num_steps = self.cost_dict[current]
                    if self.map.map_dict[node] == '*':
                        new_num_dynamites, new_num_steps = num_dynamites_needed+1, num_steps + land_cost
                    elif self.map.map_dict[node] == '~':
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + sea_cost
                    else:
                        new_num_dynamites, new_num_steps = num_dynamites_needed, num_steps + land_cost
                    # If it isn't in the open set, calculate the G and H score for the node
                    self.cost_dict[node] = (new_num_dynamites, new_num_steps)
                    self.heuristic_dict[node] = self.get_cost(node, target)
                    # Set the parent to our current item
                    self.parent_dict[node] = current
                    # Add it to the set
                    openset.add(node)
        # Throw an exception if there is no path
        self.cost_dict = {}
        self.heuristic_dict ={}
        self.parent_dict = {}
        return

    def path_to_output(self, path):
        # print(path)
        x_n, y_n = path[1]
        x_d = x_n - self.x
        y_d = y_n - self.y
        direction=None
        if x_d == -1 and y_d == 0:
            direction = 2
        elif x_d == 1 and y_d == 0:
            direction = 0
        elif x_d == 0 and y_d == 1:
            direction = 3
        elif x_d == 0 and y_d == -1:
            direction = 1
        if self.direction == direction:
            if self.map.map_dict[(x_n, y_n)] == 'k':
                self.have_key = True
                self.key_locations.remove((x_n, y_n))
                self.map.map_dict[(x_n, y_n)] = ' '
            if self.map.map_dict[(x_n, y_n)] == '$':
                self.got_treasure = True
                self.treasure_location = None
                self.map.map_dict[(x_n, y_n)] = ' '
            if self.map.map_dict[(x_n, y_n)] == 'a':
                self.have_axe = True
                self.axe_locations.remove((x_n, y_n))
                self.map.map_dict[(x_n, y_n)] = ' '
            if self.map.map_dict[(x_n, y_n)] == 'd':
                self.have_dynamite += 1
                self.dynamite_locations.remove((x_n,y_n))
                self.map.map_dict[(x_n, y_n)] = ' '
            if self.map.map_dict[(x_n, y_n)] == 'T':
                if self.have_axe:
                    self.map.map_dict[(x_n, y_n)] = ' '
                    self.tree_locations.remove((x_n,y_n))
                    self.have_boat=True
                    return 'c'
                else:
                    self.have_dynamite -= 1
                    self.map.map_dict[(x_n, y_n)] = ' '
                    return 'b'
            elif self.map.map_dict[(x_n, y_n)] == '-':
                self.map.map_dict[(x_n, y_n)] = ' '
                return 'u'
            elif self.map.map_dict[(x_n, y_n)] == '*':
                self.have_dynamite -= 1
                self.map.map_dict[(x_n, y_n)] = ' '
                return 'b'
            else:
                if self.map.map_dict[(x_n, y_n)] != '~' and self.map.map_dict[(self.x, self.y)] == '~':
                    self.have_boat = False
                    self.on_boat = False
                if self.map.map_dict[(x_n, y_n)] == '~' and self.map.map_dict[(self.x, self.y)] != '~':
                    self.have_boat = False
                    self.on_boat = True
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

    def update_map_after_use_item(self, action):
        if self.direction == 1:
            if self.map.map_dict[(self.x, self.y - 1)] not in self.item[action]:
                return
            self.map.map_dict[(self.x, self.y - 1)] = ' '
        if self.direction == 3:
            if self.map.map_dict[(self.x , self.y + 1)] not in self.item[action]:
                return
            self.map.map_dict[(self.x, self.y + 1)] = ' '
        if self.direction == 0:
            if self.map.map_dict[(self.x + 1, self.y )] not in self.item[action]:
                return
            self.map.map_dict[(self.x + 1, self.y )] = ' '
        if self.direction == 2:
            if self.map.map_dict[(self.x - 1, self.y )] not in self.item[action]:
                return
            self.map.map_dict[(self.x - 1, self.y )] = ' '

    def update_map(self, window, action):
        #print((self.x,self.y),self.direction)
        if len(self.map.map_dict) == 0:
            self.map.map_dict = copy.deepcopy(window)
            for loc in self.map.map_dict:
                if self.map.map_dict[loc] == 'k':
                    self.key_locations.add(loc)
                elif self.map.map_dict[loc] == 'T':
                    self.tree_locations.add(loc)
                elif self.map.map_dict[loc] == 'a':
                    self.axe_locations.add(loc)
                elif self.map.map_dict[loc] == '$':
                    self.treasure_location = loc
                elif self.map.map_dict[loc] == 'd':
                    self.dynamite_locations.add(loc)
                elif self.map.map_dict[loc] == '~':
                    self.sea_locations.add(loc)

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
                    self.y -= 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or self.map.map_dict[(self.x, self.y)] == '-':
                        self.y += 1
                        return
                    if self.map.map_dict[self.x,self.y] == 'd' or self.map.map_dict[self.x,self.y] == 'k' or self.map.map_dict[self.x,self.y] == 'a':
                        self.map.map_dict[self.x,self.y] = ' '
                    if self.y - 2< self.map.South_board:
                        self.map.South_board -= 1
                    for i in range(-2, 3):
                        loc=(self.x + i,self.y - 2)
                        #if loc not in self.map.map_dict:
                        self.map.map_dict[loc] = window[(i, -2)]
                        if window[(i, -2)]== 'k':
                            self.key_locations.add(loc)
                        elif window[(i, -2)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(i, -2)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(i, -2)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(i, -2)] == '~':
                            self.sea_locations.add(loc)
                        elif window[(i, -2)] == '$':
                            self.treasure_location = loc
                if self.direction == 3:
                    self.y += 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.y -= 1
                        return
                    if self.map.map_dict[self.x,self.y] == 'd' or self.map.map_dict[self.x,self.y] == 'k' or self.map.map_dict[self.x,self.y] == 'a':
                        self.map.map_dict[self.x,self.y] = ' '
                    if self.y + 2 > self.map.North_board:
                        self.map.North_board += 1
                    for i in range(-2, 3):
                        loc = (self.x - i , self.y + 2)
                        #if loc not in self.map.map_dict:
                        self.map.map_dict[loc] = window[(i, -2)]
                        if window[(i, -2)]== 'k':
                            self.key_locations.add(loc)
                        elif window[(i, -2)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(i, -2)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(i, -2)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(i, -2)] == '~':
                            self.sea_locations.add(loc)
                        elif window[(i, -2)] == '$':
                            self.treasure_location = loc
                if self.direction == 0:
                    self.x += 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.x -= 1
                        return
                    if self.map.map_dict[self.x,self.y] == 'd' or self.map.map_dict[self.x,self.y] == 'k' or self.map.map_dict[self.x,self.y] == 'a':
                       self.map.map_dict[self.x,self.y] = ' '
                    if self.x + 2> self.map.East_board:
                        self.map.East_board += 1
                    for i in range(-2, 3):
                        loc = (self.x + 2, self.y + i)
                        #if loc not in self.map.map_dict:
                        self.map.map_dict[loc] = window[(i, -2)]
                        if window[(i, -2)]== 'k':
                            self.key_locations.add(loc)
                        elif window[(i, -2)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(i, -2)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(i, -2)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(i, -2)] == '~':
                            self.sea_locations.add(loc)
                        elif window[(i, -2)] == '$':
                            self.treasure_location = loc
                if self.direction == 2:
                    self.x -= 1
                    if self.map.map_dict[(self.x, self.y)] == '*' or self.map.map_dict[(self.x, self.y)] == 'T' or \
                                    self.map.map_dict[(self.x, self.y)] == '-':
                        self.x += 1
                        return
                    if self.map.map_dict[self.x,self.y] == 'd' or self.map.map_dict[self.x,self.y] == 'k' or self.map.map_dict[self.x,self.y] == 'a':
                        self.map.map_dict[self.x,self.y] = ' '
                    if self.x - 2 < self.map.West_board:
                        self.map.West_board -= 1
                    for i in range(-2, 3):
                        loc = (self.x - 2, self.y - i)
                        #if loc not in self.map.map_dict:
                        self.map.map_dict[loc] = window[(i, -2)]
                        if window[(i, -2)]== 'k':
                            self.key_locations.add(loc)
                        elif window[(i, -2)] == 'd':
                            self.dynamite_locations.add(loc)
                        elif window[(i, -2)] == 'a':
                            self.axe_locations.add(loc)
                        elif window[(i, -2)] == 'T':
                            self.tree_locations.add(loc)
                        elif window[(i, -2)] == '~':
                            self.sea_locations.add(loc)
                        elif window[(i, -2)] == '$':
                            self.treasure_location=loc
            # else:
            #     self.update_map_after_use_item(action)
            #print((self.x,self.y),self.direction)

class Map:
    def __init__(self):
        self.South_board = 0
        self.North_board = 0
        self.East_board = 0
        self.West_board = 0
        self.map_dict = {}

    def print_map(self):
        for y in range(self.North_board, self.South_board - 1, -1):
            for x in range(self.West_board, self.East_board + 1):
                if (x, y) in self.map_dict:
                    # print((x,y), end = '')
                    print(self.map_dict[(x, y)], end='')
                else:
                    print('!', end='')
            print()

    def print_map_n(self,current):
        for y in range(self.North_board, self.South_board - 1, -1):
            for x in range(self.West_board, self.East_board + 1):
                if (x, y) in self.map_dict:
                    if (x,y)==current:
                        print('A', end='')
                    # print((x,y), end = '')
                    else:
                        print(self.map_dict[(x, y)], end='')
                else:
                    print('!', end='')
            print()

count = 0
window = {}
action = None
robot = Agent()
while True:
    print()
    for y in range(-2, 3):
        for x in range(2, -3,-1):
            if not (x == 0 and y == 0):
                ch = messg.read(1)
                if not ch:
                    print('Game Over')
                    sys.exit()
                window[(x,y)] = ch
    #print(window)
    robot.update_map(window, action)
    # robot.map.print_map()
    #print(robot.path_find((0,1)))
    # action = input('action:')
    action = robot.make_decision()
    print(action)
    # if (-7,-2) in robot.map.map_dict:
    #     robot.random_walk=False
    #     robot.sail_allowed=True
    #     robot.on_boat=True
    #     print(robot.path_find((-7,-2)))
    print(robot.x,robot.y)
    count += 1
    print(count)

    Clientsocket.send(action.encode())
