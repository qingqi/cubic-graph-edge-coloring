import random
import sys
import copy
import json

from common.path import create_path
from common.multigraph import MultiGraph
from four_color.ComplexEdgeColoring import EdgeColoring


class InductionComponent(object):

    def bicycle_algorithm(self):
        errors = []
        for e in self.graph.errors:
            errors.append(e)
        
        if len(errors) != 2:
            print "errors not equal 2, return false"
            return False 

        left = errors[0]
        right = errors[1]
        (v1, v2) = left.get_endpoints()
        (v3, v4) = right.get_endpoints()
        la = left.link_color(v1)
        lb = left.link_color(v2)
        ra = right.link_color(v3)
        rb = right.link_color(v4)
        
        a, b = la, lb
        if (la, lb) == (ra, rb):
            pass
        elif (la, lb) == (rb, ra):
            v3, v4 = v4, v3
        else:
            print "Two variable not same, return false"
            return False

        left_p = create_path(self.graph, v1, b, a)
        if left_p.is_closed() != True:
            count_utility.count(-1)
            left_p.swap_colors(b, a)
            return True
        
        right_p = create_path(self.graph, v3, b, a)
        
        
        len_left = len(left_p)
        len_right = len(right_p)
        
        steps = 0

        for i in range(0, 2 * len_left):
            for j in range(0, 2 * len_right):
                if self.sub_routine_for_bicycle_algorithm(left_p, right_p):
                    count_utility.count(steps)
                    return True
                right_p.move_one_step()
                steps = steps + 1
            left_p.move_one_step()
        
        return False

    def sub_routine_for_bicycle_algorithm(self, path1, path2):
        a, b = path1.c2, path1.c1
        v1 = path1.begin
        v2 = path1.end
     
        c = 6 - a - b
        path_ac = create_path(self.graph, v1, c, a)
        path_bc = create_path(self.graph, v2, c, b)
        v_ac = []
        v_bc = []
        for ve in self.graph.vertices:
            if ve.id not in path_ac:
                v_ac.append(ve.id)
            if ve.id not in path_bc:
                v_bc.append(ve.id)
        ac_cycle = self.factor_cycle(v_ac, a, c)
        bc_cycle = self.factor_cycle(v_bc, b, c)
        cycles = ac_cycle + bc_cycle

        for x in cycles:
            x.invert_colors()
            temp = create_path(self.graph, v1, b, a)
            if temp.is_closed() != True:
                temp.invert_colors()
                return True
            x.invert_colors()
        return False

################ remove and putback part ################################

    def remove_specified_edge(self, edge):
        e_id = edge.id
        (a, b) = edge.get_endpoints()
        
        self.graph.remove_edge(e_id)
        
        loc_a = self.graph.get_position(a)
        e1 = self.graph.smooth_vertex(a)
        (x1, y1) = self.graph.get_edge(e1).get_endpoints()
        removed_1st = (a, x1, y1, loc_a)
        
        loc_b = self.graph.get_position(b)
        e2 = self.graph.smooth_vertex(b)
        (x2, y2) = self.graph.get_edge(e2).get_endpoints()
        removed_2nd = (b, x2, y2, loc_b)
        self.removed_info.append((removed_1st, removed_2nd))

    def remove_edge_on_girth(self):
        (face, cycle) = self.find_girth()        
        e_id = random.choice(face)
        edge = self.graph.get_edge(e_id)
        self.remove_specified_edge(edge)

    def putback_the_last_deleted_edge(self, try_to_color = False):
        if len(self.removed_info) == 0:
            print "nothing to putback"
            return

        removed_1st, removed_2nd = self.removed_info.pop()
        (a, x1, y1, loc_a) = removed_1st
        (b, x2, y2, loc_b) = removed_2nd
    
        self._add_vertex_and_color(removed_2nd, try_to_color)
        self._add_vertex_and_color(removed_1st, try_to_color)
        self._add_edge_and_color(a, b, try_to_color)

    def putback_for_specified_edge(self, try_to_color = False):
        while len(self.removed_info) > 0:
            self.putback_the_last_deleted_edge(try_to_color)

    def _add_vertex_and_color(self, removed_info, try_to_color = True):
        '''
            requisite: The underlaying graph must be properly colored
        '''
        (a, x, y, loc_a) = removed_info
        
        edge = self.graph.get_edge_by_endpoints(x, y)
        xc = edge.link_color(x)
        yc = edge.link_color(y)
        
        self.graph.remove_edge(edge.id)
        
        self.graph.add_vertex(a, loc_a)
        xa = self.graph.add_edge(x, a)
        ya = self.graph.add_edge(y, a)

        if try_to_color == False:
            return

        if xc not in [1, 2, 3] or yc not in [1, 2, 3]:
            print "edge is not colored"
            return

        used_color = set()
        used_color.add(xc)
        used_color.add(yc)
        
        if xc == yc:
            temp = self.graph.get_edge(ya)
            temp.color = yc
            temp = self.graph.get_edge(xa)
            temp.get_link(x).color = xc
            temp.get_link(a).color = xc % 3 + 1
        else:
            temp = self.graph.get_edge(ya)
            temp.color = yc
            temp = self.graph.get_edge(xa)
            temp.color = xc

    def _add_edge_and_color(self, vid1, vid2, try_to_color = True):
        assert len(self.graph._neighbors[vid1]) == 2
        assert len(self.graph._neighbors[vid2]) == 2
        
        if try_to_color == False:
            self.graph.add_edge(vid1, vid2)
            return
            
        vertex1 = self.graph.get_vertex(vid1)
        vertex2 = self.graph.get_vertex(vid2)

        var1 = None
        cst1 = None
        var2 = None
        cst2 = None
        
        for e in vertex1.neighbors:
            if e.is_error():
                var1 = e
            else:
                cst1 = e
        
        for e in vertex2.neighbors:
            if e.is_error():
                var2 = e
            else:
                cst2 = e
        
        assert var1.another_link_color(vid1) == cst1.color
        assert var2.another_link_color(vid2) == cst2.color
        
        eid = self.graph.add_edge(vid1, vid2)
        
        if cst1.color == cst2.color:
            cc = cst1.color
            var1.get_link(vid1).color = cc % 3 + 1
            var2.get_link(vid2).color = cc % 3 + 1
            self.graph.get_edge(eid).color = (cc + 1) % 3 + 1
        else:
            c1 = cst1.color
            c2 = cst2.color
            var1.get_link(vid1).color = c2
            var2.get_link(vid2).color = c1
            self.graph.get_edge(eid).color = 6 - c1 - c2

############## end of remove and putback part ###########################

