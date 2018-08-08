from unittest import TestCase

from qr.webengine import WebEngine


class TestWebEngine(TestCase):
	
	query = "python artificial intelligence tutorial"
	
	def test_assess_url(self):
		self.assertTrue(WebEngine.assess_url("https://www.google.com/"))
		self.assertTrue(WebEngine.assess_url("https://www.google.com"))
		self.assertTrue(WebEngine.assess_url("https://google.com"))
		self.assertFalse(WebEngine.assess_url("https://google"))
		self.assertTrue(WebEngine.assess_url("www.google.com"))
		self.assertTrue(WebEngine.assess_url("google.com"))
	
	def test_get_google(self):
		google = WebEngine.get_google()
		self.assertEqual("Google", google.name)
	
	def test_search_html(self):
		google = WebEngine.get_google()
		content = google.search_html(TestWebEngine.query)
		print(content)
		if not (content is not None and isinstance(content, str) and len(content) > 0):
			self.fail()

	def test_search_list_html(self):
		google = WebEngine.get_google()
		items = google.search_list_html(TestWebEngine.query)
		self.assertIsNotNone(items)
		self.assertTrue(isinstance(items, list))

	def test_search_list_result(self):
		google = WebEngine.get_google()
		items = google.search_list_result(TestWebEngine.query)
		self.assertIsNotNone(items)
		self.assertTrue(isinstance(items, list))
		
		print("{}: \"{}\"\n".format(google.name, TestWebEngine.query))
		for item in items:
			print("{}\n\n".format(item))
