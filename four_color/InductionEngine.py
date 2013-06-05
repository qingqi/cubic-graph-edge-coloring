from common.multigraph import MultiGraph

from four_color.common_component import CommonComponent
from four_color.cycles_component import InductionComponent

class InductionEngine(InductionComponent, CommonComponent):
    """
        Test edge coloring algorithm for bridgeless cubic graph.
    """

    def __init__(self, graph):
        '''
        '''
        self.graph = graph
        self.removed_info = []
        

    def case_test(self, round):
        while round > 0:
            
            self.remove_edge_on_girth()
            
            if not self.edge_coloring():
                raise Exception("Can not 3 coloring the induced graph")
            assert self.graph.num_errors == 0

            self.putback_the_last_deleted_edge(True)

            if not self.bicycle_algorithm():
                print self.graph.name, self.graph.to_json()
                raise Exception("bicycle_algorithm not work!")
            
            assert self.graph.num_errors == 0
            
            round -= 1
