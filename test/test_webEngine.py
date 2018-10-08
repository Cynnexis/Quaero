import argparse
from unittest import TestCase

from PIL import Image

from qr import WebEngine, assess_url

import matplotlib.pyplot as plt


class TestWebEngine(TestCase):
	
	query1 = "python artificial intelligence tutorial"
	query2 = "pentatonix daft punk youtube"
	queries = [query1, query2]
	
	def setUp(self):
		self.show_thumbnail = False
	
	def test_assess_url(self):
		self.assertTrue(assess_url("https://www.google.com/"))
		self.assertTrue(assess_url("https://www.google.com"))
		self.assertTrue(assess_url("https://google.com"))
		self.assertFalse(assess_url("https://google"))
		self.assertTrue(assess_url("www.google.com"))
		self.assertTrue(assess_url("google.com"))
	
	def test_get_google(self):
		google = WebEngine.get_google()
		self.assertEqual("Google", google.name)
	
	def test_search_html(self):
		google = WebEngine.get_google()
		for query in TestWebEngine.queries:
			content = google.search_html(query)
			print(content)
			if not (content is not None and isinstance(content, str) and len(content) > 0):
				self.fail()

	def test_search_list_html(self):
		google = WebEngine.get_google()
		for query in TestWebEngine.queries:
			items = google.search_list_html(query)
			
			print("Items:")
			for i, item in enumerate(items):
				print("\t[{}] {}".format(i, str(item).replace('\n', ' ')))
			
			self.assertIsNotNone(items)
			self.assertTrue(isinstance(items, list))
			self.assertTrue(len(items) > 0)

	def test_search_list_result(self):
		google = WebEngine.get_google()
		for query in TestWebEngine.queries:
			items = google.search_list_result(query)
			self.assertIsNotNone(items)
			self.assertTrue(isinstance(items, list))
			
			print("{}: \"{}\"\n".format(google.name, query))
			for item in items:
				print("{}\n{}\n\n".format(item.__repr__(), item.__str__()))
			
			# Get the first item with a thumbnail and display it
			if self.show_thumbnail:
				for item in items:
					if item.thumbnail is not None and isinstance(item.thumbnail, Image.Image):
						plt.imshow(item.thumbnail)
						plt.title("Example of Thumbnail ({}x{})".format(item.thumbnail.size[0], item.thumbnail.size[1]))
						plt.grid(False)
						plt.axis('off')
						plt.show()
						break
