import random
import sys

from common.path import create_path
from four_color.ComplexEdgeColoring import EdgeColoring

class CommonComponent(object):
    

    def clear_colors(self):
        self.graph.clear_colors()

    def find_girth(self):
        """
            Find a face on the graph with girth edges
            return (face, cycle)
            face: the list of edge id
            cycle: the list of vertex id
        """
        girth = sys.maxint
        face = []
        vertices = list(self.graph.vertices)
        shift = random.randint(0,len(vertices)-1)
        vertices = vertices[shift:] + vertices[:shift]
        random.shuffle(vertices)
        
        for vertex in vertices:
            s = set() # set of explored edge id
            distance = {}
            distance[vertex.id] = 0
            father = {}
            father[vertex.id] = (None, None) # (a,b) a is v_id, b is edge id
            nodes = [vertex.id] # stack for the vertices to start with
            while len(nodes) > 0:
                node = nodes.pop(0)
                v_a = self.graph.get_vertex(node)
                nbrs = list(v_a.neighbors)
                random.shuffle(nbrs)
                for edge in nbrs:
                    if not edge.id in s:
                        another = edge.get_another_vertex(node)
                        if not distance.has_key(another):
                            nodes.append(another)
                            s.add(edge.id)
                            father[another] = (node, edge.id)
                            distance[another] = distance[node] + 1
                        elif distance[another] + distance[node] + 1 < girth:
                            girth = distance[another] + distance[node] + 1

                            face = list()
                            face.append(edge.id)
                            start = father[another]
                            while start[0] is not None:
                                face.append(start[1])
                                start = father[start[0]]
                            face.reverse()
                            start = father[node]
                            while start[0] is not None:
                                face.append(start[1])
                                start = father[start[0]]

        cycle = []
        edge0 = self.graph.get_edge(face[0])
        edge1 = self.graph.get_edge(face[1])
        (a, b) = edge0.get_endpoints()
        if a in edge1.get_endpoints():
            a, b = b, a
        for e in face:
            cycle.append(a)
            a = self.graph.get_edge(e).get_another_vertex(a)
        # logger.info("girth: %s",cycle)
        return (face, cycle)

    def factor_cycle(self, vertices, x, y):
        # vertices is the v_id list
        cycles = []
        paths = []
        while len(vertices) > 0:
            s = vertices[0]
            cycle1 = []
            path = create_path(self.graph, s, x, y)
            paths.append(path)
            assert path.is_closed(), "assert path.is_closed()"
            for v in path:
                cycle1.append(v)
                vertices.remove(v)
            cycles.append(list(cycle1))
        return paths

    def factor_graph(self, x, y):
        vid_list = self.graph.vid_list
        rc = list()
        while len(vid_list) > 0:
            v = random.choice(vid_list)
            temp = create_path(self.graph, v, x, y)
            for v in temp:
                if v in vid_list:
                    vid_list.remove(v)
            if temp.is_closed():
                rc.append(temp)
        return rc

    def edge_coloring(self):
        ec = EdgeColoring(self.graph)
        self.graph.random_color()
        if ec.another_run():
            return True
        return False

    def find_two_cycle(self):
        errors = []
        for edge in self.graph.errors:
            errors.append(edge)
        
        if len(errors) != 2:
            print "errors not equal 2, return false"
            return None

        (v1, v2) = errors[0].get_endpoints()
        (x1, y1) = self.graph._positions[v1]
        (x2, y2) = self.graph._positions[v2]
        mid1 = x1 + x2
        
        (v3, v4) = errors[1].get_endpoints()
        (x3, y3) = self.graph._positions[v3]
        (x4, y4) = self.graph._positions[v4]
        mid2 = x3 + x4

        if mid1 <= mid2:
            left = errors[0]
            right = errors[1]
        else:
            left = errors[1]
            right = errors[0]

        (v1, v2) = left.get_endpoints()
        (v3, v4) = right.get_endpoints()
        la = left.link_color(v1)
        lb = left.link_color(v2)
        ra = right.link_color(v3)
        rb = right.link_color(v4)
        
        if la + lb != ra + rb:
            print "Two variable not same, return false"
            return None

        left_p = create_path(self.graph, v1, lb, la)
        if left_p.is_closed() != True:
            print "two variables are adjacent, return False"
            return None
        right_p = create_path(self.graph, v3, rb, ra)

        c = 6 - la - lb
        if c != 3:
            self.graph.swap_colors(c, 3)
            if left_p.c1 == 3:
                left_p.c1 = c;
            else:
                left_p.c2 = c;
            if right_p.c1 == 3:
                right_p.c1 = c;
            else:
                right_p.c2 = c;
        
        return (left_p, right_p)


