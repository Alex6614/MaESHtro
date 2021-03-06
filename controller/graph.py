### CODE FROM USER mVChr on StackOverflow

from collections import defaultdict
import math
import json 
import ast 

class Graph(object):
    """ Graph data structure, undirected by default. """

    def __init__(self, directed=False):
        # Represent graph as dictionary of sets. Node is key, neighbors are enumerated in set
        self._graph = defaultdict(set)
        self._directed = directed
        self.all_nodes = set() # Set of all nodes (vertices set)
        self.all_gateways = set() # Set of all gateways
        self.has_seen = set() # Set of all nodes communicated with in past x iterations of server code

    def update_seen(self, client_ip): 
        self.has_seen.add(client_ip)

    def reset_seen(self): 
        set_difference = self.all_nodes.difference(self.has_seen)
        for s in set_difference: 
            self._graph.remove(s)    # MIGHT CAUSE ERRORS?
            self.all_nodes.remove(s)
            if s in self.all_gateways: 
                self.all_gateways.remove(s)
        self.has_seen = set()

    def update_neighbors(self, client_ip, client_neighbors): 
        # If client hasn't been seen yet, add to graph
        if client_ip not in self.all_nodes: 
            self.all_nodes.add(client_ip)

        # Update client's neighbors in graph. If neighbor not in graph, add to it
        new_neighbors = set()
        for n in client_neighbors: 
            new_neighbors.add(n)
            self._graph[n].add(client_ip)
            if n not in self.all_nodes: 
                self.all_nodes.add(n)
        self._graph[client_ip] = new_neighbors

    def update_gateways(self, client_ip, is_gateway): 
        if is_gateway == True: 
            self.all_gateways.add(client_ip)
        else: 
            if client_ip in self.all_gateways: 
                self.all_gateways.remove(client_ip)

    def add_connections_list(self, connections):
        """ Add connections (list of tuple pairs) to graph """

        for node1, node2 in connections:
            self.add_connection(node1, node2)

    def add_connection(self, node1, node2):
        """ Add connection between node1 and node2 """

        self._graph[node1].add(node2)
        if not self._directed:
            self._graph[node2].add(node1)

    def remove(self, node):
        """ Remove all references to node """

        for n, cxns in self._graph.iteritems():
            try:
                cxns.remove(node)
            except KeyError:
                pass
        try:
            del self._graph[node]
        except KeyError:
            pass

    def is_connected(self, node1, node2):
        """ Is node1 directly connected to node2 """

        return node1 in self._graph and node2 in self._graph[node1]

    '''
    def find_best_gateway(self, client_ip): 
        return_gateway = ""
        return_path_length = 1000000

        for g in self.all_gateways:
            path_consider = self.find_path(client_ip, g)
            print("path consider is: ")
            print(path_consider)
            path_length = len(path_consider)
            print("length of path consider is: ")
            print(path_length)
            if path_length < return_path_length: 
                return_gateway = g
       return return_gateway
    '''

    # Now returns gateway or next hop to gateway
    def find_default_next_hop(self, client_ip): 
        q = []
        dist = {}
        prev = {}
        for v in self.all_nodes: 
            dist[v] = 100000
            prev[v] = None
            q.append(v)

        dist[client_ip] = 0

        while len(q) > 0: 
            #print("dictionary keys are: ")
            set_of_keys = set(dist.keys())
            #print(set_of_keys)
            set_of_queue = set(q)
            intersection = set_of_queue.intersection(set_of_keys)
            #print("intersection set is: ")
            #print(intersection)

            #u = min(dist, key=dist.get)
            min_dist = 100000
            for i in intersection: 
                if dist[i] < min_dist: 
                    min_dist = dist[i]
                    u = i


            #print("u is: ")
            #print(u)
            q.remove(u)
            neighbors = self._graph[u]
            #print("neighbors are: ")
            #print(neighbors)

            for v in neighbors: 
                alt = dist[u] + 1
                if alt < dist[v]: 
                    dist[v] = alt
                    prev[v] = u

        min_dist_gateway = 100000
        return_gateway = ""
        for g in self.all_gateways: 
            if dist[g] < min_dist_gateway: 
                return_gateway = g
        #return return_gateway
        print("Best gateway is: ")
        print(return_gateway)
        while prev[return_gateway] != client_ip: 
            return_gateway = prev[return_gateway]

        print("Next hop is: ")
        print(return_gateway)
        return return_gateway


    # Find all info to give to gateway node
    def find_next_hop_for_all_nodes(self, client_ip): 
        return_list = []
        q = []
        dist = {}
        prev = {}
        for v in self.all_nodes: 
            dist[v] = 100000
            prev[v] = None
            q.append(v)

        dist[client_ip] = 0

        while len(q) > 0: 
            #print("dictionary keys are: ")
            set_of_keys = set(dist.keys())
            #print(set_of_keys)
            set_of_queue = set(q)
            intersection = set_of_queue.intersection(set_of_keys)
            #print("intersection set is: ")
            #print(intersection)

            u = min(dist, key=dist.get)
            min_dist = 100000
            for i in intersection: 
                if dist[i] < min_dist: 
                    min_dist = dist[i]
                    u = i


            #print("u is: ")
            #print(u)
            q.remove(u)
            neighbors = self._graph[u]
            #print("neighbors are: ")
            #print(neighbors)

            for v in neighbors: 
                alt = dist[u] + 1
                if alt < dist[v]: 
                    dist[v] = alt
                    prev[v] = u

        min_dist_gateway = 100000
        return_gateway = ""
        for g in self.all_gateways: 
            if dist[g] < min_dist_gateway: 
                return_gateway = g
        #return return_gateway
        print("Best gateway is: ")
        print(return_gateway)

        if return_gateway == client_ip: 
            return_gateway = ""
        else: 
            while prev[return_gateway] != client_ip: 
                return_gateway = prev[return_gateway]

            print("Next hop is: ")
            print(return_gateway)

        for dest_node in self.all_nodes:
            if dest_node != client_ip: 
                next_hop = dest_node
                while prev[next_hop] != client_ip: 
                    next_hop = prev[next_hop]

                #print("Destination node is: ")
                #print(dest_node)
                #print("Next hop is: ")
                #print(next_hop)

                s = tuple((dest_node, next_hop))
                return_list.append(s)
        
        return_json = {}
        return_json['default'] = return_gateway
        return_json['next_hops'] = return_list
        json_data = json.dumps(return_json)
        # print(json_data)
        return json_data


    def find_path(self, node1, node2, path=[]):
        """ Find any path between node1 and node2 (may not be shortest) """
        print("in find_path function in graph.py")
        path = path + [node1]
        if node1 == node2:
            print("returning path in find_path function")
            return path
        if node1 not in self._graph:
            print("node1 not in self._graph")
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path(node, node2, path)
                if new_path:
                    print("returning new_path")
                    return new_path
        return None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))

'''
graph = Graph()
connections = [("2", "1"), ("1", "2"), ("1", "3"), ("3", "1"), ("1", "0"), ("0", "1"), ("0", "4"), ("4", "0"), ("0", "3"), ("3", "0")]
graph.add_connections_list(connections)
print(graph._graph)

graph.all_nodes.add("0")
graph.all_nodes.add("1")
graph.all_nodes.add("2")
graph.all_nodes.add("3")
graph.all_nodes.add("4")

graph.all_gateways.add("3")

j = graph.find_next_hop_for_all_nodes("3")
print("json is: ")
print(j)

parsed_json = ast.literal_eval(j)
next_hops = parsed_json["next_hops"]
for n in next_hops: 
    print(n)
    print(n[0])
    print(n[1])
'''