import os

BASE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE, 'data')
DB_FILE = os.path.join(DATA_DIR, 'graphs.db')
DB_FILE_FOR_FAILED_GRAPH = os.path.join(DATA_DIR,'failedGraphs.db')
#DB_FILE_FOR_FAILED_GRAPH = os.path.join(DATA_DIR,'allcubicGraphs.db')
SNARK_GRAPH = os.path.join(DATA_DIR,'snarkGraphs.db')
SNARK_GRAPH_2 = os.path.join(DATA_DIR,'snarkGraphs1.db')
VIEW_THIS_DB = DB_FILE_FOR_FAILED_GRAPH
#VIEW_THIS_DB = SNARK_GRAPH
#os.path.join(DATA_DIR,'snarkGraphs.db') 



class Stat():
	def __init__(self):
		self.stats = dict()

	def count(self, x):
		if self.stats.has_key(x):
			self.stats[x] = self.stats[x] + 1
		else:
			self.stats[x] = 1

	def print_out(self):
		for x in self.stats:
			print x, ": ", self.stats[x]


count_utility = Stat()