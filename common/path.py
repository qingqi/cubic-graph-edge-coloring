import logging


class Path(object):
    def __init__(self, graph, c1, c2):
        self._graph = graph
        self.c1 = c1
        self.c2 = c2
        self._vertices = []
        self._closed = False
        
    def __iter__(self):
        for v in self._vertices:
            yield v

    def __str__(self):
        return ' -- '.join([str(v) for v in self._vertices])

    def __len__(self):
        return len(self._vertices)

    def __contains__(self, v):
        return v in self._vertices

    def set_closed(self, closed = True):
        self._closed = closed

    def is_closed(self):
        return self._closed

    def validate(self):
        color = self.c1
        alt_color = self.c2
        for i in range(0, len(self._vertices)-1):
            temp = self._graph.get_edge_by_endpoints(self._vertices[i], self._vertices[i+1])
            if temp.color != color:
                raise Exception("Path internal error!")
            color, alt_color = alt_color, color
        temp = self._graph.get_edge_by_endpoints(self._vertices[0], self._vertices[-1])
        if temp.link_color(self._vertices[0]) != self.c2:
            raise Exception("Path internal error 2")
        if temp.link_color(self._vertices[-1]) != color:
            raise Exception("Path internal error 3")

    @property
    def begin(self):
        return self._vertices[0]

    @property
    def end(self):
        return self._vertices[-1]

    def add_vertex(self, v, position = "end"):
        if v in self._vertices:
            if position == "end" and v == self._vertices[0]:
                self._closed = True
            elif position == "begin" and v == self._vertices[-1]:
                self._closed = True
            return False
        if position == "end":
            self._vertices.append(v)
        elif position == "begin":
            self._vertices.insert(0, v)
        return True

    def swap_colors(self, c1, c2):
        self.c1, self.c2 = self.c2, self.c1
        for i in self._vertices:
            v = self._graph.get_vertex(i)
            v.swap_colors(c1, c2)

    def invert_colors(self):
        self.c1, self.c2 = self.c2, self.c1
        for i in self._vertices:
            v = self._graph.get_vertex(i)
            v.swap_colors(self.c1, self.c2)

    def move_one_step(self):
        if self._closed == True:
            v = self._graph.get_vertex(self._vertices[0])
            v.swap_colors(self.c1, self.c2)
            self.c1, self.c2 = self.c2, self.c1
            self._vertices = self._vertices[1:] + self._vertices[:1]
        else:
            print "error"

    def move_steps(self, num = 1):
        if self._closed == False:
            print "error"
            return
        if num > 0:
            while num > 0:
                num = num - 1
                v = self._graph.get_vertex(self._vertices[0])
                v.swap_colors(self.c1, self.c2)
                self.c1, self.c2 = self.c2, self.c1
                self._vertices = self._vertices[1:] + self._vertices[:1]
        elif num < 0:
            while num < 0:
                num = num + 1
                v = self._graph.get_vertex(self._vertices[-1])
                v.swap_colors(self.c1, self.c2)
                self.c1, self.c2 = self.c2, self.c1
                self._vertices = self._vertices[-1:] + self._vertices[:-1]

    @property
    def edges(self):
        ret = list()
        for i in range(0, len(self._vertices) - 1):
            ret.append(self._graph.get_edge_by_endpoints(self._vertices[i], self._vertices[i+1]))
        if self._closed == True:
            ret.append(self._graph.get_edge_by_endpoints(self._vertices[0], self._vertices[-1]))
        return ret

    @property
    def variable(self):
        if self._closed != True:
            return None
        if len(self._vertices) % 2 == 0:
            return None
        return self.graph.get_edge_by_endpoints(self._vertices[0], self._vertices[-1])



def create_path(multigraph, va, c1, c2):
    '''
        this method searches a c1 - c2 kempe path start from va and with color c1
        until it meets a variable or the path is closed
        (The variable is not in the resulting path unless it closes the kempe path)

    '''
    p = Path(multigraph, c1, c2)
    p.add_vertex(va)
    vertex = multigraph.get_vertex(va)
    color = c1
    alt_color = c2

    while True:
        edge = vertex.get_neighbor_edge_by_color(color)
        if edge is None:
            break

        vb = edge.get_another_vertex(va)
        if vb in p:
            if vb == p.begin and edge.get_link(vb).color in [c1, c2]:
                p.set_closed()
            break

        elif edge.is_error():
            break

        p.add_vertex(vb)
        va = vb
        vertex = multigraph.get_vertex(va)
        color, alt_color = alt_color, color

    return p

def create_maximal_path(multigraph, vid, c1, c2):
    p = Path(multigraph, c1, c2)
    va = vid
    p.add_vertex(va)
    vertex = multigraph.get_vertex(va)
    color = c1
    alt_color = c2

    while True:
        edge = vertex.get_neighbor_edge_by_color(color)
        if edge is None:
            break

        vb = edge.get_another_vertex(va)
        if vb in p:
            if vb == p.begin and edge.get_link(vb).color in [c1, c2]:
                p.set_closed()
            break

        elif edge.is_error():
            break

        p.add_vertex(vb)
        va = vb
        vertex = multigraph.get_vertex(va)
        color, alt_color = alt_color, color

    color = c2
    alt_color = c1
    while True:
        edge = vertex.get_neighbor_edge_by_color(color)
        if edge is None:
            break

        vb = edge.get_another_vertex(va)
        if vb in p:
            if vb == p.end and edge.get_link(vb).color in [c1, c2]:
                p.set_closed()
            break
        elif edge.is_error():
            break

        p.add_vertex()
    return p
