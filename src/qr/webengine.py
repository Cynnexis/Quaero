# -*- coding: utf-8 -*-
import os
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup, Tag
from typing import Union, Optional, List

from qr.webresult import WebResult


class WebEngine:
	
	def __init__(self, name: str, home_url: str, pattern_search_url: str):
		if not isinstance(name, str) or len(name) == 0:
			raise TypeError("name must be a non-empty string")
		
		if not self.assess_url(home_url):
			raise TypeError("The home url '{}' is not a valid url".format(home_url))
		
		if not self.assess_url(pattern_search_url.format("")):
			raise TypeError("The pattern search url '{}' is not a valid url".format(pattern_search_url.format("")))
		
		self._name = name
		self._home_url = home_url
		self._pattern_search_url = pattern_search_url
	
	@staticmethod
	def assess_url(url: str) -> bool:
		regex = re.compile(r'^((?:http|ftp)?s?://)?'  # http:// or https://
		                   r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
		                   r'localhost|'  # localhost...
		                   r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
		                   r'(?::\d+)?'  # optional port
		                   r'(?:/?|[/?]\S+)$', re.IGNORECASE)
		return re.match(regex, url) is not None
	
	def search_html(self, keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]]) \
		-> Optional[str]:
		attributes = ""
		
		if isinstance(keywords, str) or isinstance(keywords, int) or isinstance(keywords, float) or \
				isinstance(keywords, complex):
			keywords = [str(keywords)]
		
		for keyword in keywords:
			if len(attributes) != 0:
				attributes += ' '
			attributes += str(keyword)
		
		attributes = urllib.parse.urlencode({"attributes": attributes}).split('=')[1]
		
		if self.name.lower() == "qwant":
			attributes = attributes.replace('+', "%20")
		
		url = self.pattern_search_url.format(attributes)
		
		req = urllib.request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
		content = None
		with urllib.request.urlopen(req) as f:
			content = f.read().decode("utf-8")
		
		if os.getenv("DEBUG", False):
			self.__write_html_debug(content)
		
		return content
	
	def search_list_html(self, keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]], result_as_str: bool = True) \
		-> Optional[Union[List[str], List[Tag]]]:
		
		content = self.search_html(keywords)
		soup = BeautifulSoup(content, features="html.parser")
		
		if self.name.lower() == "google" and False:
			containers = soup.find("div", {"class": "srg"})
			
			if containers is None:
				containers = soup.find("div", {"id": "ires"})
				
				if containers is None:
					self.__write_html_debug(content)
					return None
				
				containers = containers.find("ol")
				
				if containers is None:
					self.__write_html_debug(content)
					return None
			
			divs_g = containers.find_all("div", {"class": 'g'})
			
			items = []
			for div in divs_g:
				if result_as_str:
					items.append(str(div))
				else:
					items.append(div)
			
			return items
		else:
			containers = soup.find_all("ol")
			if containers is None or len(containers) == 0:
				containers = soup.find_all("ul")
				
				if containers is None or len(containers) == 0:
					raise TypeError("Not configured yet. Please try to make a search with google")
			
			# Search for the container such that ine of its items contains the keywords
			if not isinstance(keywords, list):
				keywords = [keywords]
			max_match = 0
			max_i = 0
			i = 0
			while i < len(containers):
				list_keywords = ' '.join(map(str, keywords))
				match = re.findall(list_keywords, str(containers[i]))
				if len(match) > max_match:
					max_match = len(match)
					max_i = i
				i += 1
			
			# Search the container is the one with the highest matches
			container: Tag = containers[max_i]
			
			html_items = container.contents
			for html_item in html_items:
				if len(html_item) == 1:
					html_nested_item = html_item.find_all()
					print("{} -> {}".format(html_item.name, html_nested_item))
				else:
					print("{}".format(html_item))
			
			return html_items
		
		return None
	
	def search_list_result(self, keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]]) \
		-> Optional[List[WebResult]]:
		
		items = self.search_list_html(keywords, result_as_str=False)
		
		results = []
		
		if self.name.lower() == "google":
			for i in items:
				h3_r = i.find("h3", {"class": 'r'})
				
				if h3_r is None:
					continue
				
				# Get url
				h3_r_a = h3_r.find('a')
				part_url = h3_r_a["href"]
				
				# Add '/' if there is none
				if not self.home_url.endswith('/'):
					part_url = '/' + part_url
				
				url = self.home_url + part_url
				
				# Get title
				title = str(h3_r_a.contents[0])
				
				# Get description
				div_s = i.find("div", {"class", 's'})
				
				if div_s is None:
					description = ""
				else:
					div_st = div_s.find("span", {"class", 'st'})
					description = str(div_st.contents[0])
				
				results.append(WebResult(title, url, "", description))
			
			return results
		else:
			raise TypeError("Not configured yet. Please try to make a search with google")
		
		return None
	
	search = search_list_result
	
	@staticmethod
	def __write_html_debug(content: str):
		with open("../../out/debug.html", 'w') as f:
			f.write(content)
	
	# BUILDERS #
	
	@staticmethod
	def get_google():
		return WebEngine(name="Google", home_url="https://www.google.com/",
		                 pattern_search_url="https://www.google.fr/search?q={}&ie=UTF-8&oe=UTF-8")
	
	@staticmethod
	def get_bing():
		return WebEngine(name="Bing", home_url="https://www.bing.com/",
		                 pattern_search_url="https://www.bing.com/search?q={}")
	
	@staticmethod
	def get_yahoo():
		return WebEngine(name="Bing", home_url="https://www.yahoo.com/",
		                 pattern_search_url="https://www.search.yahoo.com/search?p={}&ei=UTF-8")
	
	@staticmethod
	def get_duckduckgo():
		return WebEngine(name="DuckDuckGo", home_url="https://duckduckgo.com/",
		                 pattern_search_url="https://duckduckgo.com/?q={}")
	
	@staticmethod
	def get_qwant():
		return WebEngine(name="Qwant", home_url="https://www.qwant.com/",
		                 pattern_search_url="https://www.qwant.com/?q={}")
	
	# GETTERS & SETTERS #
	
	@property
	def name(self):
		return self._name
	
	@name.setter
	def name(self, name):
		self._name = name
	
	@property
	def home_url(self):
		return self._home_url
	
	@home_url.setter
	def home_url(self, home_url):
		self._home_url = home_url
	
	@property
	def pattern_search_url(self):
		return self._pattern_search_url
	
	@pattern_search_url.setter
	def pattern_search_url(self, pattern_search_url):
		self._pattern_search_url = pattern_search_url
	
	# OVERRIDES #
	
	def __eq__(self, o: object) -> bool:
		return isinstance(o, WebEngine) and self.name == o.name and self.home_url == o.home_url and \
		       self.pattern_search_url == o.pattern_search_url
	
	def __str__(self) -> str:
		return self.__repr__()
	
	def __repr__(self) -> str:
		return "WebEngine{name='{}', home_url='{}', pattern_search_url='{}'}".format(self.name, self.home_url,
		                                                                             self.pattern_search_url)
