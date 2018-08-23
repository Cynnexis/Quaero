# -*- coding: utf-8 -*-
import urllib
import urllib.request
from typing import Union, Optional, List, Any

from bs4 import Tag, Comment, PageElement, BeautifulSoup, Doctype
from typeguard import *

from qr.keywords_error import KeywordsError
from qr.webengine import WebEngine
from qr.information import Info
from qr.webutils import assess_url

from qr.webresult import WebResult


class Searcher:
	"""
	Search information on a website.
	"""
	
	# CONSTRUCTOR
	
	@typechecked
	def __init__(self, website: Optional[Union[str, WebResult]] = None):
		"""
		Constructor of Searcher.
		:param website: The website to search on. It can either be an URL to the website, the HTML content of the
		website or a WebResult (given by WebEngine).
		:type website: Union[str, WebResult, None]
		"""
		if website is None:
			website = None

		# Configure website
		website = self.__convert_website(website)
		
		self._website = website
	
	# SEARCHER METHODS #
	
	@typechecked
	def search(self, website: Optional[Union[str, WebResult]] = None,
	           keywords: Optional[Union[str, List[Union[str, int, float, complex, int, float, complex]]]] = None,
	           web_engine: Optional[WebEngine] = None) \
			-> Info:
		
		# If 'website' is None, get the one from the constructor (if given)
		if website is None:
			website = self.get_website()
		
		# If 'web_engine' is None, get Google
		if web_engine is None:
			web_engine = WebEngine.get_google()
		
		# At least one argument must be given
		if website is None and keywords is None:
			raise TypeError("'website' and 'keywords' cannot be both None")
		
		# If 'website' is None but 'keyword' is not, then research on the given web engine
		if website is None and keywords is not None:
			results = web_engine.search_list_result(keywords)
			if len(results) > 0:
				website = results[0]
				website = self.__convert_website(website)
				with open("../../out/searcher_first_result.html", 'w') as f:
					f.write(website)
			else:
				raise KeywordsError("Cannot find any results with the following keywords: {}".format(keywords))
		
		# If 'website' is not None but keywords is, then search any content in the given website:
		if website is not None and keywords is None:
			return self.__search_anything(website)
		
		# if both 'website' and 'keywords' are not None, then search thoroughly
		if website is not None and keywords is not None:
			return self.__search_thoroughly(website, keywords)
	
	@typechecked
	def __search_anything(self, website: Union[str, WebResult]) -> Info:
		website = self.__convert_website(website)
		return Info()
	
	@typechecked
	def __search_thoroughly(self, website: Union[str, WebResult],
	                        keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]]) \
			-> Info:
		"""
		See https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
		:param website:
		:param keywords:
		:return:
		"""
		
		hidden_tags = ["head", "title", "meta", "script", "style", "[document]"]
		
		def is_tag_visible(tag: PageElement) -> bool:
			return not (isinstance(tag, Tag) and (tag.name in hidden_tags or tag.parent.name in hidden_tags)) or \
			       isinstance(tag, Comment)
		
		def extract_text(html: Union[BeautifulSoup, str]) -> List[str]:
			if isinstance(html, str):
				html = BeautifulSoup(html, features="html.parser")
			
			# Extract useless tags
			[soup.extract() for soup in html.contents if isinstance(soup, Doctype)]
			for hidden_tag in hidden_tags:
				[soup.extract() for soup in html(hidden_tag)]
			
			texts = html.find_all(text=True)
			visible_tags = list(filter(is_tag_visible, texts))
			for i, tag in enumerate(visible_tags):
				visible_tags[i] = visible_tags[i].strip()
			visible_tags = list(filter(lambda element: element != '', visible_tags))
			return list(tag.strip() for tag in visible_tags)
		
		website = self.__convert_website(website)
		print(extract_text(website))
		return Info()
	
	@typechecked
	def __convert_website(self, website: Optional[Union[str, WebResult]]) -> Optional[str]:
		"""
		Configure the given argument such that it returns the HTML content of the given website
		:param website: The website to convert.
		:type website: Union[str, WebResult, None]
		:return: Union[str, None]
		"""
		def get_html_content(url: str) -> str:
			req = urllib.request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
			content = ""
			with urllib.request.urlopen(req) as f:
				content = f.read().decode("utf-8")
			return content
		
		if website is None:
			return None
		elif isinstance(website, WebResult):
			website = website.url
		
		if isinstance(website, str):
			# If the website is an url, download the page
			if assess_url(website):
				return get_html_content(website)
			else:
				return website
		else:
			return None
	
	# GETTER & SETTER #
	
	@typechecked
	def get_website(self) -> Optional[str]:
		return self._website
	
	@typechecked
	def set_website(self, website: Optional[Union[str, WebResult]]):
		self._website = self.__convert_website(website)
	
	website = property(get_website, set_website)
	
	# OVERRIDES #
	
	def __eq__(self, other):
		if other is None or not isinstance(other, Searcher):
			return False
		
		return self.website == other.website
	
	def __str__(self):
		# TODO: Make a custom __str__ method
		return self.__repr__()
	
	def __repr__(self):
		return "Searcher{{website='{}'}}".format(self.website)
