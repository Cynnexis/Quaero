from unittest import TestCase

from qr import Searcher


class TestSearcher(TestCase):
	
	def setUp(self):
		self.searcher = Searcher()
	
	def test_search(self):
		self.searcher.search(keywords=["python", "debugger"])
