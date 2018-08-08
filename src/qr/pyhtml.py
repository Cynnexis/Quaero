# -*- coding: utf-8 -*-
from html.parser import HTMLParser
from typing import Dict, Union, Optional, List

from qr.element import Element


class PyHTML:
	
	def __init__(self, content: str):
		self._content = content
		self._root = None
		self.parse()
	
	def parse(self, content: str = None):
		if content is None:
			content = self.content
			
			if content is None:
				raise TypeError("Cannot feed with None.")
		
		class MyHTMLParser(HTMLParser):
			
			def handle_decl(self, decl):
				print("Declaration: {}".format(decl))
			
			def handle_starttag(self, tag, attrs):
				print("Start tag {} (attrs: {})".format(tag, attrs))
			
			def handle_endtag(self, tag):
				print("End tag {}".format(tag))
			
			def handle_startendtag(self, tag, attrs):
				print("Start/End tag {} (attrs: {})".format(tag, attrs))
			
			def handle_data(self, data):
				data = data.replace(' ', '').replace('\t', '').replace("\r\n", '').replace("\n", '')
				print("Data: {}".format(data))
			
			def handle_pi(self, data):
				print("Process: {}".format(data))
			
			def unknown_decl(self, data):
				print("Unknown declaration: {}".format(data))
		
		parser = MyHTMLParser()
		parser.feed(content)
		
		print()
	
	def feed(self, content: str = None):
		if content is None:
			content = self.content
			
			if content is None:
				raise TypeError("Cannot feed with None.")
		
		# Transform content into a list such as:
		# "<body><p>test<br/></p></body>" -> ["<body>", "<p>", "test", "<br/>", "</p>", "</body>"]
		
		content = content.replace("\t", "").replace("\r\n", "").replace("\n", "").strip()
		
		tags = []
		
		in_tag = False
		current = ""
		i = 0
		l_content = list(content)
		while i < len(l_content):
			c = l_content[i]
			
			if c == '<':
				if in_tag:
					raise ValueError("The given content is not a valid HTML text.")
				else:
					in_tag = True
					
					# If text has been captured, then save it
					if current != "" and current != tags[-1]:
						tags.append(current)
					
					current = c
			elif c == '>':
				if not in_tag:
					raise ValueError("The given content is not a valid HTML text.")
				else:
					in_tag = False
					current += c
					tags.append(current)
					current = ""
			else:
				current += c
			
			i = i + 1
		
		print("tags = {}".format(tags))
		self.__feed_rec(tags, self._root)
	
	def __feed_rec(self, tags: List[str], elem: Element) -> Optional[Element]:
		"""
		Fill the elements tree using the tags
		:param tags: The list containing all remaining tags to add to the tree
		:param elem: The element where element.content will be filled using 'tags'. Thus, the other attribute of element
		must have been initialized previously
		:return: The tree
		"""
		
		def get_attrs(tag: str):
			raw_attrs = tag.replace('/>', '').replace('>', '').replace('\t', '').replace("\r\n", '').replace('\n', '').split(' ')[1:]
			attrs = {}
			for raw_attr in raw_attrs:
				key = raw_attr.split('=')[0]
				if len(raw_attr.split('=')) > 0:
					value = raw_attr.split('=')[1]
					if value.startswith('"'):
						value = value.split('"')[1]
					elif value.startswith("'"):
						value = value.split("'")[1]
					
					if value.endswith('"'):
						value = value.split('"')[0]
					elif value.endswith("'"):
						value = value.split("'")[0]
				else:
					value = ""
				attrs[key] = value
			return attrs
		
		if tags is None or len(tags) == 0:
			return None
		
		tag = tags[0]
		
		# Parse elem.content such that it becomes a list of string
		if elem.content is None:
			elem.content = []
		elif not isinstance(elem.content, list):
			elem.content = [elem.content]
		
		e = None
		# If the current tag is a special tag (declaration)...
		if tag.startswith("<!"):
			name = tag.replace("<!", '').split(' ')[0].split("\r\n")[0].split('\n')[0].split('!>')[0].split('/>')[0].split('>')[0]
			e = Element(tag=name, attrs=get_attrs(tag), content=None, is_tag_empty=True)
		# If the current tag is a PHP tag...
		elif tag.startswith("<?"):
			name = tag.replace("<?", '').split(' ')[0].split("\r\n")[0].split('\n')[0].split('?>')[0].split('/>')[0].split('>')[0]
			e = Element(tag=name, attrs=get_attrs(tag), content=None, is_tag_empty=True)
		# If the current tag is an empty tag (like "<br/>")...
		elif tag.startswith('<') and tag.endswith('/>'):
			name = tag.replace('<', '').split(' ')[0].split("\r\n")[0].split('\n')[0].split('/>')[0]
			e = Element(tag=name, attrs=get_attrs(tag), content=None, is_tag_empty=True)
		# Else, if the current tag is a normal tag...
		else:
			name = tag.replace('<', '').split(' ')[0].split("\r\n")[0].split('\n')[0].split('>')[0]
			# Search the other end of the tag through 'tags'
			tags_like_current = 0
			i = 1
			remaining = list(tags[1:])  # Copy the instance of 'tags' and delete first item in the new one
			for r in remaining:
				r_name = r.replace('<', '').split(' ')[0].split("\r\n")[0].split('\n')[0].split('>')[0]
				if r.replace(' ', '').strip() == "<{}/>".format(name):
					break
				elif r == name:
					tags_like_current += 1
				i += 1
			
			# 'i' is the index of the end of the current tag in 'tags'
			print("The end of <{}> is located at {}: {}".format(name, i, tags[i]))
			
			# Delete it
			del tags[i]
			
			# All tags between 0 and 'i' (both not included) must be in elem.content
			elem = self.__feed_rec(tags[1:i-1], )
			
			
		
		# [...]
		return self.__feed_rec(tags[1:], elem)
	
	# GETTERS & SETTERS #
	
	@property
	def content(self):
		return self._content
	
	@content.setter
	def content(self, value):
		self._content = value
		self.parse()
	
	@property
	def root(self):
		return self._root
	
	@root.setter
	def root(self, value):
		self._root = value
	
	# OVERRIDES #
	
	def __str__(self) -> str:
		return self.__repr__()
	
	def __repr__(self) -> str:
		return self.content
	
	def __getitem__(self, key):
		return self.root[key]

# def __setitem__(self, key, value):
# 	self.root[key] = value
