# This class defines multi-children tree node

class TreeNode(object):

    def __init__(self, value):
        self.parent = None
        self.value = value
        self.children = set([])

    def is_root(self):
        return self.parent is None

    def add_child(self, child):
        self.children.add(child)
        child.parent = self

    def get_path(self):
        path = []
        node = self
        path.append(node)

        while not node.is_root():
            node = node.parent
            path.append(node)
            
        return [node.value for node in path]
