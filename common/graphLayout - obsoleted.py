'''
This module is obsolete. Feel free to ignore it. However, if you are seeking any inspiration, you may want to read it.

But, I have compiled it rigorously.
'''
import os
import pydot
import tempfile
import logging
import json
from subprocess import Popen, PIPE
from common.multigraph import MultiGraph
from common.path import create_path


import random
import logging


logger = logging.getLogger(__name__)


def find_neato():
    cmds = pydot.find_graphviz()
    if cmds is not None:
        if cmds.has_key('neato'):
            return cmds['neato']


class GraphLayoutEngine(object):

    @classmethod
    def layout(cls, graph, width=600, height=600, margin=20):
        #    from formats import DotWriter
        colors = ['red', 'green', 'blue', 'orange', 'cyan']
        def write_graph(g, f):
            graph = pydot.Dot(graph_type='graph')
            graph.set_prog('neato')
            node = pydot.Node()
            node.set_name('node')
            node.set('shape', 'point')
            graph.add_node(node)

            for e in g.edges:
                (l1, l2) = e.links
                (v1, v2) = e.vertices
                edge = pydot.Edge(str(v1.id), str(v2.id))
                if not e.is_error():
                    edge.set('color', colors[l1.color])
                graph.add_edge(edge)
            f.write(graph.to_string())


        graph._positions = {}
        f = tempfile.NamedTemporaryFile(delete=False)
        write_graph(graph, f)
        f.close()
        filename = f.name

        neato_cmd = find_neato()
        if neato_cmd is None:
            logging.error('cannot find neato')
            raise Exception('cannot find neato, check graphviz installation')

        s = Popen([neato_cmd, '-Gepsilon=0.001', filename], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()[0]
        layout_f = tempfile.NamedTemporaryFile(delete=False)
        layout_f.write(s)
        layout_f.close()
        g = pydot.graph_from_dot_file(layout_f.name)

        vertices = []
        w = width - margin * 2.0
        h = height - margin * 2.0
        ratio = 1
        for v in g.get_nodes():
            name = v.get_name()
            if name == 'graph':
                if v.get_attributes().has_key('bb'):
                    bb = v.get_attributes()['bb']
                    bb = bb[1:-1].split(',')
                    w = float(bb[2])
                    h = float(bb[3])
                    ratio = min((width - margin * 2) / w, (height - margin * 2) / h)
            try:
                if int(name) > 0:
                    pos = v.get_pos()
                    xy = pos[1:-1].split(',')
                    x = float(xy[0])
                    y = float(xy[1])
                    vertices.append({'x': x, 'y': y, 'name': name})
            except:
                pass

        for vertex in vertices:
            x = int(vertex['x'] * ratio + margin)
            y = int(vertex['y'] * ratio + margin)
            v_id = int(vertex['name'])
            graph._positions[v_id] = (x, y)


    @classmethod
    def standard_format(cls, graph, width=600, height=600, margin=20):
        result, err_msg, left, right, left_top, right_top, ceil = cls().find_KaiXuanMen(graph)
        if result == False:
            print err_msg
            return False

        if ceil.color != 3:
            graph.swap_colors(ceil.color,3)

        if left.link_color(left_top) != 2:
            p = create_path(graph, left_top, 2, 1)
            p.swap_colors(1, 2)
        
        if right.link_color(right_top) != 2:
            p = create_path(graph, right_top, 2, 1)
            p.swap_colors(1, 2)

        kaixuanmen = (left, right, left_top, right_top, ceil)
        cls().format_location(graph, kaixuanmen, width, height, margin)
        return True
    
    @classmethod
    def invert_left_xy(cls, graph):
        result, err_msg, left, right, left_top, right_top, ceil = cls().find_KaiXuanMen(graph)
        left_bottom = left.get_another_vertex(left_top)
        path = create_path(graph, left_top, left.link_color(left_bottom), left.link_color(left_top))
        path.swap_colors(left.link_color(left_bottom), left.link_color(left_top))

    @classmethod
    def invert_right_xy(cls, graph):
        result, err_msg, left, right, left_top, right_top, ceil = cls().find_KaiXuanMen(graph)
        right_bottom = right.get_another_vertex(right_top)
        path = create_path(graph, right_top, right.link_color(right_bottom), right.link_color(right_top))
        path.swap_colors(right.link_color(right_bottom), right.link_color(right_top))


    @classmethod
    def find_KaiXuanMen(cls, graph):
        ''' contaions only two variables of the same kind
            which are linked by a ceil edge
            and the two variables are in different kempe cycles
        '''
        errors = []
        for edge in graph.edges:
            if edge.is_error():
                errors.append(edge)
        if len(errors) != 2:
            err_msg = "errors not equal 2, return false"
            return (False, err_msg, None, None, None, None, None) 

        left = errors[0]
        right = errors[1]
        (la, lb) = left.links
        (ra, rb) = right.links
        if la.color + lb.color != ra.color + rb.color:
            err_msg = "Two variable not same, return false"
            return (False, err_msg, None, None, None, None, None)

        ceil = None
        (la, lb) = left.get_endpoints()
        (ra, rb) = right.get_endpoints()
        
        if graph.get_edge_by_endpoint(la, ra) != None:
            left_top, right_top = la, ra
            ceil = graph.get_edge_by_endpoint(left_top, right_top)

        if graph.get_edge_by_endpoint(la, rb) != None:
            left_top, right_top = la, rb
            ceil = graph.get_edge_by_endpoint(left_top, right_top)

        if graph.get_edge_by_endpoint(lb, ra) != None:
            left_top, right_top = lb, ra
            ceil = graph.get_edge_by_endpoint(left_top, right_top)

        if graph.get_edge_by_endpoint(lb, rb) != None:
            left_top, right_top = lb, rb
            ceil = graph.get_edge_by_endpoint(left_top, right_top)
            
        if ceil == None:
            err_msg = "format color failed! Two variable not adjacent, return false"
            return (False, err_msg, None, None, None, None, None)


        left_p = create_path(graph, left_top, left.link_color(left.get_another_vertex(left_top)), left.link_color(left_top))
        if left_p.is_closed() != True:
            err_msg = "left path not closed. Two variables are linked by kempe path, return false"
            return (False, err_msg, None, None, None, None, None)

        return (True, "", left, right, left_top, right_top, ceil)
    

    @classmethod
    def format_location(cls, graph, kaixuanmen, width=600, height=600, margin=20):
        left, right, left_top, right_top, ceil = kaixuanmen
        radius = width
        import math
        rad = 2 * math.asin( 0.5 * float(height - 2 * margin) / radius )
        
        left_p = create_path(graph, left_top, left.link_color(left.get_another_vertex(left_top)), left.link_color(left_top))
        for index in range(0, len(left_p), 1):
            p_rad = index * rad / (len(left_p)-1)
            p_y = margin + (height - 2 * margin) / 2 - math.sin(rad / 2 - p_rad) * radius
            p_x = margin + math.cos(rad /2 - p_rad) * radius - math.cos(rad / 2) * radius
            graph._positions[left_p._vertices[index]] = (p_x, p_y)
       
        right_p = create_path(graph, right_top, right.link_color(right.get_another_vertex(right_top)), right.link_color(right_top))
        for index in range(0, len(right_p), 1):
            p_rad = index * rad / (len(right_p)-1)
            p_y = margin + (height - 2 * margin) /2 - math.sin(rad / 2 - p_rad) * radius
            p_x = width - margin - (math.cos(rad / 2 - p_rad) * radius - math.cos(rad / 2) * radius)
            graph._positions[right_p._vertices[index]] = (p_x, p_y)

        (la, lb) = left.links
        color_a = la.color
        color_b = lb.color

        other_vertices = []
        for vertex in graph._vertices:
            if (vertex not in left_p) and (vertex not in right_p):
                other_vertices.append(int(vertex))
         
        cycle = []
        while len(other_vertices) > 0:
            start = other_vertices[0]
            p = create_path(graph, start, color_a, color_b)
            for x in p._vertices:
                other_vertices.remove(int(x))
            cycle.append(p._vertices)

        x0 = width / 2
        step = (height - 2 * margin) / (len(cycle) + 1)
        for i in range(0,len(cycle),1):
            y0 = margin + (i + 1) * step
            step_angle = 2 * math.pi / len(cycle[i])
            for j in range(0, len(cycle[i]), 1):
                x = x0 + math.cos(j * step_angle) * (width - 2 * margin)/4
                y = y0 + math.sin(j * step_angle) * (width - 2 * margin)/4
                graph._positions[cycle[i][j]] = (x,y)


    
    @classmethod
    def alternate_ceil(cls, graph, width=600, height=600, margin=20):
        result, err_msg, left, right, left_top, right_top, ceil = cls().find_KaiXuanMen(graph)
        if result == False:
            print err_msg
            return False
        
        cc = ceil.color
        bb = left.link_color(left_top)
        graph.get_vertex(left_top).swap_colors(cc,bb)
        graph.get_vertex(right_top).swap_colors(cc,bb)
        result, err_msg, left, right, left_top, right_top, ceil = cls().find_KaiXuanMen(graph)
        if result == False:
            print err_msg
            return False
        kaixuanmen = (left, right, left_top, right_top, ceil)
        cls().format_location(graph, kaixuanmen, width, height, margin)
        return True


    
class DotWriter(object):

    colors = ['red', 'green', 'blue', 'orange', 'cyan']
    file_extensions = ['dot']

    @staticmethod
    def write_graph(g, f):
        import pydot
        graph = pydot.Dot(graph_type='graph')
        graph.set_prog('neato')
        node = pydot.Node()
        node.set_name('node')
        node.set('shape', 'point')
        graph.add_node(node)

        for e in g.edges:
            (l1, l2) = e.links
            (v1, v2) = e.vertices
            edge = pydot.Edge(str(v1.id), str(v2.id))
            if not e.is_error():
                edge.set('color', DotWriter.colors[l1.color])
            graph.add_edge(edge)
        #graph.write_png('test.png', prog='neato')
        f.write(graph.to_string())

