# -*- coding: utf-8 -*-
from typing import Union, Optional, List, Any
from typeguard import *

from qr.webengine import WebEngine
from qr.information import Info
from qr.webutils import assess_url

from qr.webresult import WebResult


class Searcher:
	
	# CONSTRUCTOR
	
	@typechecked
	def __init__(self, website: Optional[Union[str, WebResult]] = None):
		if website is None:
			website = None
		
		self._website = website
		
		# Configure website
		self.set_website(website)
	
	# SEARCHER METHODS #
	
	@typechecked
	def search(self, website: Optional[Union[str, WebResult]] = None,
	           keywords: Optional[Union[str, List[Union[str, int, float, complex, int, float, complex]]]] = None) \
			-> Info:
		
		# If 'website' is None, get the one from the constructor (if given)
		if website is None:
			website = self.get_website()
		
		# At least one argument must be given
		if website is None and keywords is None:
			raise TypeError("'website' and 'keywords' cannot be both None")
		
		# If 'website' is None but 'keyword' is not, then research on Google
		if website is None and keywords is not None:
			results = WebEngine.get_google().search_list_result(keywords)
			if len(results) > 0:
				website = results[0]
				website = self.__convert_website(website)
		
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
	                        keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]])\
			-> Info:
		website = self.__convert_website(website)
		keywords()
		return Info()
	
	@typechecked
	def __convert_website(self, website: Optional[Union[str, WebResult]]) -> Optional[str]:
		if website is None:
			return None
		elif isinstance(website, str):
			return website
		elif isinstance(website, WebResult):
			return website.url
	
	# GETTER & SETTER #
	
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
