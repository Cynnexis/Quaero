# -*- coding: utf-8 -*-
from typing import Union, Optional, List
from typeguard import *

from qr.searcher import Searcher
from qr.information import Info
from qr.webengine import WebEngine
from qr.webresult import WebResult


class Quaero:
	
	# CONSTRUCTOR #
	
	@typechecked
	def __init__(self, web_engine: Union[WebEngine, str, None] = None):
		if web_engine is None:
			web_engine = WebEngine.get_google()
		elif isinstance(web_engine, str):
			web_engine = web_engine.lower().strip()
			if web_engine == "google":
				web_engine = WebEngine.get_google()
			elif web_engine == "bing":
				web_engine = WebEngine.get_bing()
			elif web_engine == "yahoo":
				web_engine = WebEngine.get_yahoo()
			elif web_engine.replace(' ', '') == "duckduckgo":
				web_engine = WebEngine.get_duckduckgo()
			elif web_engine == "qwant":
				web_engine = WebEngine.get_qwant()
			else:
				raise ValueError("No web engine found with the name '{}'. Please use 'google', 'bing', 'yahoo', "
				                 "'duckduckgo' or 'qwant'".format(web_engine))
		
		self._web_engine = web_engine
	
	# QUAERO METHOD #
	
	@typechecked
	def search(self, keyword: Union[str, List[Union[str, int, float, complex, int, float, complex]]],
	           website: Optional[Union[str, WebResult]] = None) -> Info:
		s = Searcher(website)
		return s.search(keywords=keyword, web_engine=self._web_engine)
	
	# GETTER & SETTER #
	
	@typechecked
	def get_web_engine(self) -> WebEngine:
		if self._web_engine is None:
			self._web_engine = WebEngine.get_google()
		
		return self._web_engine
	
	@typechecked
	def set_web_engine(self, web_engine: WebEngine):
		self._web_engine = web_engine
	
	web_engine = property(get_web_engine, set_web_engine)
	
	# OVERRIDES #
	
	def __eq__(self, other):
		if other is None or not isinstance(other, Quaero):
			return False
		
		return self.web_engine == other.web_engine
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __str__(self):
		return "Quaero instance using {} web engine".format(self.web_engine.name)
	
	def __repr__(self):
		return "Quaero{{web_engine='{}'}}".format(repr(self.web_engine))
