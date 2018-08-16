# -*- coding: utf-8 -*-
from typing import Union, Optional, List
from typeguard import *

from qr.webengine import WebEngine


class Quaero:
	
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
	
	def search(self, keyword: Union[str, List[str]]):
		pass
