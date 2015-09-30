from four_color.InductionEngine import InductionEngine
from common.storage import failed_graph_DB
from common.multigraph import MultiGraph

class GraphMerger(object):
    """:class:`GraphMerger` builds a larger graph by merging two small graphs.

    """

    @classmethod
    def merge(cls, g1, g2):
        inspector1 = InductionEngine(g1)
        inspector2 = InductionEngine(g2)
        (face1, cycle1) = inspector1.find_girth()
        (face2, cycle2) = inspector2.find_girth()
        if len(face1) != len(face2):
            print "two face not of same kind"
            return None
        
        graph = MultiGraph()
        v_count = 1
        v1_map = {}
        v2_map = {}
        for u in g1.vertices:
            v1_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1
        for u in g2.vertices:
            v2_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1
        
        for edge in g1.edges:
            (a, b) = edge.get_endpoints()
            if a in cycle1 and b in cycle1:
                continue
            graph.add_edge(v1_map[a], v1_map[b])
        
        for edge in g2.edges:
            (a, b) = edge.get_endpoints()
            if a in cycle2 and b in cycle2:
                continue
            graph.add_edge(v2_map[a], v2_map[b])
        
        k = min(len(cycle1), len(cycle2))
        cycle1.append(cycle1[0])
        cycle2.append(cycle2[0])
        for i in xrange(k):
            x, y = tuple(map(v1_map.get, cycle1[i:i + 2]))
            u, v = tuple(map(v2_map.get, cycle2[i:i + 2]))
            p = v_count
            q = v_count + 1
            v_count += 2
            graph.add_vertex(p)
            graph.add_vertex(q)
            graph.add_edge(x, p)
            graph.add_edge(p, y)
            graph.add_edge(p, q)
            graph.add_edge(u, q)
            graph.add_edge(q, v)

        for i in xrange(k, len(cycle1) - 1):
            x, y = tuple(map(v1_map.get, cycle1[i:i + 2]))
            if graph.multiplicity(x, y) == 0:
                graph.add_edge(x, y)

        for i in xrange(k, len(cycle2) - 1):
            x, y = tuple(map(v2_map.get, cycle2[i:i + 2]))
            if graph.multiplicity(x, y) == 0:
                graph.add_edge(x, y)
        return graph


    @classmethod
    def single_vertex_merge(cls, g1, g2):
        vertices_num1 = g1.num_vertices
        vertices_num2 = g2.num_vertices

        vertex_1 = g1.random_pick_a_vertex()
        vertex_2 = g2.random_pick_a_vertex()

        neighbor_vertices1 = []
        for v in vertex_1.neighbor_vertices:
            neighbor_vertices1.append(v)

        neighbor_vertices2 = []
        for v in vertex_2.neighbor_vertices:
            neighbor_vertices2.append(v)

        graph = MultiGraph()
        v_count = 1
        v1_map = {}
        v2_map = {}
        for u in g1.vertices:
            if u.id == vertex_1.id:
                continue
            v1_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1

        for u in g2.vertices:
            if u.id == vertex_2.id:
                continue
            v2_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1
        
        for edge in g1.edges:
            (a, b) = edge.get_endpoints()
            if a == vertex_1.id or b == vertex_1.id:
                continue
            graph.add_edge(v1_map[a], v1_map[b])
        
        for edge in g2.edges:
            (a, b) = edge.get_endpoints()
            if a == vertex_2.id or b == vertex_2.id:
                continue
            graph.add_edge(v2_map[a], v2_map[b])
        
        x1, y1, z1 = neighbor_vertices1[0], neighbor_vertices1[1], neighbor_vertices1[2]
        x2, y2, z2 = neighbor_vertices2[0], neighbor_vertices2[1], neighbor_vertices2[2]
        e_id1 = graph.add_edge(v1_map[x1], v2_map[x2])
        e_id2 = graph.add_edge(v1_map[y1], v2_map[y2])
        e_id3 = graph.add_edge(v1_map[z1], v2_map[z2])

        return (graph, [e_id1, e_id2, e_id3])


    @classmethod
    def single_vertex_and_edge_merge(cls, g1, g2):
        vertex_1 = g1.random_pick_a_vertex()
        edge_1 = g2.random_pick_a_edge()

        graph = MultiGraph()
        v_count = 1
        v1_map = {}
        v2_map = {}
        
        for u in g1.vertices:
            if u.id == vertex_1.id:
                continue
            v1_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1

        for u in g2.vertices:
            v2_map[u.id] = v_count
            graph.add_vertex(v_count)
            v_count += 1

        new_vertices = range(v_count, v_count + 5, 1)

        for i in new_vertices:
            graph.add_vertex(i)

        for i in range(0, 5, 1):
            graph.add_edge(new_vertices[i], new_vertices[(i+1) % 5])

        ret1 = list()
        for edge in g1.edges:
            (a, b) = edge.get_endpoints()
            
            if a == vertex_1.id:
                temp = new_vertices.pop()
                ret1.append(temp)
                graph.add_edge(v1_map[b], temp)
            elif b == vertex_1.id:
                temp = new_vertices.pop()
                ret1.append(temp)
                graph.add_edge(v1_map[a], temp)

            else:
                graph.add_edge(v1_map[a], v1_map[b])
        
        for edge in g2.edges:
            if edge.id == edge_1.id:
                continue
            (a, b) = edge.get_endpoints()
            graph.add_edge(v2_map[a], v2_map[b])

        x, y = edge_1.get_endpoints()
        graph.add_edge(new_vertices[0], v2_map[x])
        graph.add_edge(new_vertices[1], v2_map[y])

        #print "ret1: ", ret1
        #print "new vertex: ", new_vertices
        elist = list()
        elist.append((ret1[0], ret1[1]))
        elist.append((ret1[1], ret1[2]))
        elist.append((new_vertices[0], new_vertices[1]))
        
        try:
            graph.validate()
        except:
            failed_graph_DB.add_graph(graph.name, graph.to_json())
            raise
        return (graph, elist)
