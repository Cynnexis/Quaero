# -*- coding: utf-8 -*-
import os
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup, Tag
from typing import Union, Optional, List, Iterable, Tuple
from typeguard import *

from qr.webutils import assess_url
from qr.webresult import WebResult


class WebEngine:
	"""
	Class that represents a web engine, such as Google.
	"""

	@typechecked
	def __init__(self, name: str, home_url: str, pattern_search_url: str):
		if len(name) == 0:
			raise TypeError("name must be a non-empty string")
		
		if not assess_url(home_url):
			raise TypeError("The home url '{}' is not a valid url".format(home_url))
		
		if not assess_url(pattern_search_url.format("")):
			raise TypeError("The pattern search url '{}' is not a valid url".format(pattern_search_url.format("")))
		
		self._name = name
		self._home_url = home_url
		self._pattern_search_url = pattern_search_url

	@typechecked
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
		
		if os.getenv("DEBUG", False) == "True":
			self.__write_html_debug(content)
		
		return content

	@typechecked
	def search_list_html(self, keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]],
	                     result_as_str: bool = True) -> Union[List[str], List[Tag], None]:
		
		content = self.search_html(keywords)
		soup = BeautifulSoup(content, features="html.parser")
		
		if self.name.lower() == "google":
			divs_g = soup.find_all("div", {"class": 'g'})
			items = []
			for div in divs_g:
				items.append(str(div) if result_as_str else div)
			
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
			container = containers[max_i]
			
			html_items = container.contents
			for html_item in html_items:
				if len(html_item) == 1:
					html_nested_item = html_item.find_all()
					print("{} -> {}".format(html_item.name, html_nested_item))
				else:
					print("{}".format(html_item))
			
			if result_as_str:
				html_items = map(str, html_items)
			
			return html_items
		
		return None

	@typechecked
	def search_list_result(self, keywords: Union[str, List[Union[str, int, float, complex, int, float, complex]]]) \
		-> Optional[List[WebResult]]:
		
		items = self.search_list_html(keywords, result_as_str=False)
		if isinstance(keywords, Iterable):
			list_keywords = ' '.join(map(str, keywords))
		else:
			list_keywords = keywords
		
		results = []
		
		if self.name.lower() == "google":
			for i in items:
				h3_r = i.find("h3", {"class": 'r'})
				
				if h3_r is None:
					# In case the result is in big-thumbnail-format
					h3_r = i.find("h3", {"class": "p9j1ue"})
					
					if h3_r is None:
						# Worst-case scenario
						h3_r = i.find("h3")
						
						# Very-worst-case scenario
						if h3_r is None:
							continue
				
				# Get url
				h3_r_a = h3_r.find('a')
				
				if h3_r_a is None:
					continue
				elif not h3_r_a.has_attr("href"):
					continue
				
				part_url = h3_r_a["href"]
				
				# Add '/' if there is none
				if not self.home_url.endswith('/'):
					part_url = '/' + part_url
				# Remove '/' if it is both on 'home_url' and 'part_url'
				if self.home_url.endswith('/') and part_url.startswith('/'):
					part_url = part_url[1:]
				
				# Construct the URL
				url = self.home_url + part_url
				
				# Get title
				title = str(self.remove_tags(h3_r_a.text))
				
				# Get date
				span_st = i.find("span", {"class": 'st'})
				
				date = ""
				if span_st is not None:
					span_f = span_st.find("span", {"class": 'f'})
					
					if span_f is not None:
						span_nobr = span_f.find("span", {"class": "nobr"})
						
						if span_nobr is not None:
							date = self.remove_tags(span_nobr.text)
				
				# Get description
				if span_st is not None:
					# Extract the date (don't need it anymore)
					[s.extract() for s in span_st("span", {"class": 'f'})]
					description = self.remove_tags(span_st.text, True)
				else:
					description = ""
				
				# Get the thumbnail
				img = i.find("img")
				
				thumbnail = None
				if img is not None:
					if img.has_attr("src"):
						thumbnail = img["src"]
						# Reconstruct the URL if it is a partial URL
						if thumbnail.startswith('/'):
							# Add '/' if there is none
							if not self.home_url.endswith('/'):
								part_thumbnail = '/' + part_thumbnail
							
							# Construct the URL
							thumbnail = self.home_url + part_thumbnail
				
				results.append(WebResult(title=title, url=url, thumbnail=thumbnail, date=date, description=description))
			
			return results
		else:
			item = items[0]
			tags = item.find_all()
			print("Tags:")
			for i, tag in enumerate(tags):
				print("\t[{}] {}".format(i, tag))
			
			for i, item in enumerate(items):
				tags = item.find_all()
				
				# Find title
				title = ""
				possible_titles = List[Tuple[int, float, str]] # nb_keywords, nb_keywords/nb_words_total, possible_title
				a_s = item.find_all('a')
				# Search every possible title and the number of keywords inside it
				for a in a_s:
					possible_title = self.remove_tags(a.content)
					match = re.findall(list_keywords, possible_title)
					nb_keywords = len(match) if match is not None else 0
					nb_words = len(possible_title.split())
					possible_titles.append((nb_keywords, nb_keywords/nb_words, possible_title))
				
				# Search the best title (where possible_titles[i][1] is max
				max = 0.
				for possible_title in possible_titles:
					if possible_title[1] > max:
						max = possible_title[1]
						title = possible_title[2]
				
				# Search URL
				hrefs = []
				for a in item.find_all('a'):
					if a.has_attr("href"):
						if assess_url(a["href"]):
							hrefs.append(a["href"])
				
				# Delete duplicate
				hrefs = list(set(hrefs))
				
				possible_urls = []
				list_keywords_lower = '|'.join(list_keywords).lower().split('|')
				for href in hrefs:
					match = re.findall(list_keywords_lower, href)
					nb_keywords = len(match) if match is not None else 0
					possible_urls.append((nb_keywords, href))
				
				possible_urls = list(set(possible_urls))
				
				url = sorted(possible_urls, key=lambda x: x[0])[-1]
				
				# Search description
				description = ""
				
			raise TypeError("Not configured yet. Please try to make a search with google")
		
		return None
	
	search = search_list_result
	
	@staticmethod
	@typechecked
	def remove_tags(message: str, replace_br_by_newline: bool = False) -> str:
		if replace_br_by_newline:
			message = re.sub(r'</?br[\s]*/?>', '\n', message)
		return re.sub(r'</?[^>]*/?>', '', message)
	
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
	def name(self) -> str:
		return self._name
	
	@name.setter
	@typechecked
	def name(self, name: str):
		self._name = name
	
	@property
	def home_url(self) -> str:
		return self._home_url
	
	@home_url.setter
	@typechecked
	def home_url(self, home_url: str):
		self._home_url = home_url
	
	@property
	def pattern_search_url(self) -> str:
		return self._pattern_search_url
	
	@pattern_search_url.setter
	@typechecked
	def pattern_search_url(self, pattern_search_url: str):
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
