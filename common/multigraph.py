'''
This is the most important module in this project. Please read it carefully. Including:
class MultiGraph, Vertex, Edge, Link

'''
import logging
import json
import random
import Queue
from common.path import create_path

# Internal parameter to represent the maximum number of edges in MultiGraph
MAX_NUMBER_OF_EDGES = 10000 

logger = logging.getLogger(__name__)

class MultiGraph(object):
    def __init__(self, name = 'Untitled'):
        self._vertices = [] # list of vertex id
        self._edges = {} # edge_id ==> tuple of (vertex_id, vertex_id)
        self._neighbors = {} # vertex_id => list of edge_id
        self._colors = {} # (edge_id, vertex_id) => color
        self._positions = {} # vertex_id => (x, y)
        self.name = name
        
        # Initialize the queue for management of edge id
        self.priority_queue = Queue.PriorityQueue()
        self.priority_queue.queue = range(1, MAX_NUMBER_OF_EDGES + 1, 1)
         

######################################################
#          Add and miscellaneous
######################################################
    def add_vertex(self, v_id, position = (0,0)):
        """Add a vertex with the given id to the graph.
        This method does nothing if there is already a vertex
        with the given id on this graph.
        """
        if type(v_id) != int:
            raise Exception("Input v_id is not int")

        if not (type(position) == tuple and len(position) == 2):
            raise Exception("Error position input, should be (x, y)")

        if v_id not in self._vertices:
            self._vertices.append(v_id)
            self._neighbors[v_id] = []
            self._positions[v_id] = position
            
   
    def add_edge(self, a, b, color = 0):
        """
        Add a edge with end vertex "a" and "b", and colored with "color"
        """
        if type(a) != int or type(b) != int:
            raise Exception("a or b is not int")

        if a == b:
            raise Exception("no loop is allowed")
        
        if a > b:
            a, b = b, a

        if self.priority_queue.empty():
            raise Exception("edge id is used up!")

        e_id = self.priority_queue.get()
        self._edges[e_id] = (a, b)
        self._neighbors[a].append(e_id)
        self._neighbors[b].append(e_id)
        
        self.set_color(e_id, a, color)
        self.set_color(e_id, b, color)
        
        return e_id

    @classmethod
    def from_json(cls, content):
        """
         read a graph from json content (content is a string)
        """
        graph = cls()
        data = json.loads(content)
        for vertex in data['vertices']: 
            graph.add_vertex(int(vertex['name']), (int(vertex['x']), int(vertex['y'])))

        for edge in data['edges']:
            e_id = graph.add_edge(int(edge['v1']), int(edge['v2']))
            graph.set_color(e_id, int(edge['v1']), int(edge['c1']))
            graph.set_color(e_id, int(edge['v2']), int(edge['c2']))
        
        return graph

    def to_json(self):
        edges = []
        for edge in self.edges:
            (a, b) = edge.get_endpoints()
            edges.append({
                'v1': a,
                'v2': b,
                'c1': edge.get_link(a).color,
                'c2': edge.get_link(b).color,
                })

        vertices = []
        for vertex in self.vertices:
            x, y = self._positions[vertex.id]
            data = {
                'x': x,
                'y': y,
                'name': vertex.id
            }
            vertices.append(data)

        return json.dumps({'edges': edges, 'vertices': vertices})

    def to_dot(self):
        colors = ['black', 'red', 'blue', 'gray']
        s = 'graph G {\nnode [shape=circle, style=filled, width=0.05, fixedsize=true]; \n'
        for edge in self.edges:
            (a, b) = edge.get_endpoints()
            s += '%d -- %d [color="%s"];\n' % (a, b, colors[edge.color])
        s += '}'
        return s

    def validate(self):
        """
        validate whether it is a cubic graph
        """
        for v in self._vertices:
            assert len(self._neighbors[v]) == 3
        return True

    def __iter__(self):
        """
        Return a iterator passing through all nodes in the graph.
        
        @rtype:  iterator
        @return: Iterator passing through all nodes in the graph.
        """
        for n in self._vertices:
            yield n
            
    def __getitem__(self, node):
        """ 
        Return a iterator passing through all neighbors of the given node.
        
        @rtype:  iterator
        @return: Iterator passing through all neighbors of the given node.
        """
        neighbor_vertices  = set()
        eid_list = self._neighbors[node]
        for n in eid_list:
            (a, b) = self._edges[n]
            if a == node:
                neighbor_vertices.add(b)
            else:
                neighbor_vertices.add(a)
        for x in neighbor_vertices:
            yield x


######################################################
#          Delete and Modify
######################################################

    def remove_edge(self, e_id):
        if not e_id in self._edges:
            return
        a, b = self._edges[e_id]
        del self._edges[e_id]
        self._neighbors[a].remove(e_id)
        self._neighbors[b].remove(e_id)
        del self._colors[(e_id, a)]
        del self._colors[(e_id, b)]
        self.priority_queue.put(e_id)

    def delete_vertex(self, v_id):
        if v_id not in self._vertices:
            raise Exception{"v_id is not in the graph"}

        while len(self._neighbors[v_id]) > 0:
            self.remove_edge(self._neighbors[v_id][0])

        del self._neighbors[v_id]
        del self._positions[v_id]
        self._vertices.remove(v_id)

    
    def smooth_vertex(self, v_id):
        """
        Remove the vertex and keep the graph cubic.
        Allow multi edges.
        """
        assert len(self._neighbors[v_id]) == 2
        
        e_b = self._neighbors[v_id][0]
        b = self.get_edge(e_b).get_another_vertex(v_id)
        
        e_c = self._neighbors[v_id][1]
        c = self.get_edge(e_c).get_another_vertex(v_id)
        
        self.delete_vertex(v_id)
        e_id = self.add_edge(b, c)
        
        return e_id

    
    def clear_colors(self):
        for e in self._colors:
            self._colors[e] = 0

    def set_color(self, e_id, a, c):
        if a in self.get_edge(e_id):
            self._colors[(e_id, a)] = c

    def swap_colors(self, c1, c2):
        for v in self.vertices:
            v.swap_colors(c1, c2)

    def random_color(self):
        for a in self._vertices:
            n = len(self._neighbors[a])
            colors = range(1, n + 1)
            random.shuffle(colors)
            for i in xrange(n):
                e_id = self._neighbors[a][i]
                self.set_color(e_id, a, colors[i])


######################################################
#          Query
######################################################

    @property
    def edges(self):
        for e_id in self._edges:
            yield self.get_edge(e_id)

    @property
    def vertices(self):
        for v_id in self._vertices:
            yield self.get_vertex(v_id)

    @property
    def errors(self):
        for edge in self.edges:
            if edge.is_error():
                yield edge

    @property
    def eid_list(self):
        relt = []
        for x in self._edges:
            relt.append(x)
        return relt

    @property 
    def vid_list(self):
        relt = []
        for x in self._vertices:
            relt.append(x)
        return relt

    @property
    def num_errors(self):
        return len(list(self.errors))
    
    @property
    def num_vertices(self):
        return len(self._vertices)

    @property
    def num_edges(self):
        return len(self._edges)


    def get_vertex(self, v_id):
        if v_id in self._vertices:
            return Vertex(self, v_id)
        return None
    
    def get_edge(self, e_id):
        if e_id in self._edges:
            return Edge(self, e_id)
        return None

    def get_position(self, v_id):
        return self._positions[v_id]

    def random_pick_a_vertex(self):
        if len(self._vertices) > 0:
            temp = random.choice(self._vertices)
            return Vertex(self, temp)

    def random_pick_a_edge(self):
        if len(self._edges) > 0:
            temp = random.sample(self._edges, 1)
            return Edge(self, temp[0])

    def neighbor_vid_list(self, vid):
        ret = list()
        elist = self._neighbors[vid]
        for eid in elist:
            (a, b) = self._edges[eid]
            if a == vid:
                ret.append(b)
            elif b == vid:
                ret.append(a)
            else:
                raise Exception("MultiGraph internel errors")
        return ret

    def neighbor_eid_list(self, v_id):
        if v_id in self._neighbors:
            return self._neighbors[v_id]
        return []

    def get_edge_endpoints(self, e_id):
        if e_id in self._edges:
            return self._edges[e_id]
        return None

    def get_edges(self, a, b):
        e_list = list()
        for x in self._edges:
            if (a, b) == self._edges[x] or (b, a) == self._edges[x]:
                e_list.append(Edge(self, x))
        return e_list

    def get_edge_by_endpoints(self, a, b, color = None):
        '''
        if there are multiple edges, you can specify which one by 'color'
        '''
        if color == None:
            for x in self._edges:
                if (a, b) == self._edges[x] or (b, a) == self._edges[x]:
                    return Edge(self, x)
        else:
            for x in self._edges:
                if (a, b) == self._edges[x] or (b, a) == self._edges[x]:
                    if self._colors[(x, a)] == color and self._colors[(x, b)] == color:
                        return Edge(self, x)
        return None

    def multiplicity(self, a, b):
        mul = 0
        for x in self._edges:
            if (a, b) == self._edges[x] or (b, a) == self._edges[x]:
                mul = mul + 1
        return mul

    def get_link(self, e_id, a):
        if e_id in self._edges and a in self.get_edge(e_id):
            return Link(self, e_id, a)

    def get_color(self, e_id, a):
        if (e_id, a) in self._colors:
            return self._colors[(e_id, a)]
        return -1



class Vertex(object):
    def __init__(self, graph, v_id):
        self.graph = graph
        self.id = v_id

    @property
    def neighbors(self):
        for e_id in self.graph.neighbor_eid_list(self.id):
            yield self.graph.get_edge(e_id)

    @property
    def neighbor_vertices(self):
        for edge in self.neighbors:
            yield edge.get_another_vertex(self.id)

    @property
    def links(self):
        for e_id in self.graph.neighbor_eid_list(self.id):
            yield self.graph.get_link(e_id, self.id)

    def swap_colors(self, c1, c2):
        a = self.id
        for link in self.links:
            if link.color == c1:
                link.color = c2
            elif link.color == c2:
                link.color = c1

    def get_neighbor_edge_by_color(self,c):
        a = self.id
        for link in self.links:
            if link.color == c:
                return link.edge
        return None

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.id == other.id


class Edge(object):
    def __init__(self, graph, e_id):
        self.graph = graph
        self.id = e_id
        a, b = self.graph.get_edge_endpoints(e_id)
        self.vertex_a_id = a
        self.vertex_b_id = b

    def __contains__(self, v_id):
        return self.vertex_a_id == v_id or self.vertex_b_id == v_id

    @property 
    def edge_type(self):
        x = self.graph.get_color(self.id, self.vertex_a_id)
        y = self.graph.get_color(self.id, self.vertex_b_id)
        if x == y:
            return "constant"
        elif x + y == 3:
            return "ab"
        elif x + y == 4:
            return "ac"
        elif x + y == 5:
            return "bc"
        else:
            return "unknown"

    def link_color(self, v_id):
        link = self.get_link(v_id)
        if link != None:
            return link.color
        else:
            return -1

    def another_link_color(self, v_id):
        if v_id == self.vertex_a_id:
            link = self.get_link(self.vertex_b_id)
            if link != None:
                return link.color
        elif v_id == self.vertex_b_id:
            link = self.get_link(self.vertex_a_id)
            if link != None:
                return link.color
        return -1

    def get_endpoints(self):
        return (self.vertex_a_id, self.vertex_b_id)

    
    def get_vertex(self, v_id):
        if v_id == self.vertex_a_id or v_id == self.vertex_b_id:
            return self.graph.get_vertex(v_id)
        else:
            return None

    def get_link(self, v_id):
        if v_id == self.vertex_a_id or v_id == self.vertex_b_id:
            return self.graph.get_link(self.id, v_id)
        else:
            return None

    @property
    def links(self):
        la = self.graph.get_link(self.id, self.vertex_a_id)
        lb = self.graph.get_link(self.id, self.vertex_b_id)
        return (la, lb)

    @property
    def vertices(self):
        va = self.graph.get_vertex(self.vertex_a_id)
        vb = self.graph.get_vertex(self.vertex_b_id)
        return (va, vb)
  
    def is_error(self):
        (la, lb) = self.links
        return la.color != lb.color

    def get_another_vertex(self, v_id):
        if v_id == self.vertex_b_id:
            return self.vertex_a_id
        if v_id == self.vertex_a_id:
            return self.vertex_b_id
        raise Exception("this vertex is not on the edge")

    @property
    def color(self):
        (la, lb) = self.links
        if la.color == lb.color:
            return la.color
        else:
            return -1

    @color.setter
    def color(self, c):
        (la, lb) = self.links
        la.color = c
        lb.color = c


class Link(object):
    def __init__(self, graph, e_id, v_id):
        self.graph = graph
        self.edge_id = e_id
        self.vertex_id = v_id

    @property
    def color(self):
        return self.graph.get_color(self.edge_id, self.vertex_id)

    @color.setter
    def color(self, c):
        self.graph.set_color(self.edge_id, self.vertex_id, c)

    @property
    def edge(self):
        return self.graph.get_edge(self.edge_id)

    @property
    def vertex(self):
        return self.graph.get_vertex(self.vertex_id)


