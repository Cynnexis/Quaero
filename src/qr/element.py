# -*- coding: utf-8 -*-
from typing import Optional, Union, Dict


class Element:
	
	# CONSTRUCTOR #
	
	def __init__(self, tag: str = "p", attrs: Optional[Dict[str, str]] = None,
	             content: Optional[Union['Element', str]] = None, is_tag_empty: bool = False):
		self.tag = tag
		self.attrs = attrs
		self.content = content
		self.is_tag_empty = is_tag_empty
	
	# ELEMENT METHODS #
	
	def get_tag(self, tag_name: str) -> Union[str, 'Element']:
		if self.content is None:
			raise TypeError("Cannot find any tag in this element.")
		
		if isinstance(self.content, Element) and self.content.tag == tag_name:
			return self.content
		elif isinstance(self.content, list):
			for item in self.content:
				if isinstance(item, Element) and item.tag == tag_name:
					return item
		
		raise IndexError("Cannot find \'{}\' as tag.".format(tag_name))
	
	def get_tag_or_default(self, tag_name: str, default_value: object = None) -> Union[str, 'Element', object]:
		try:
			return self.get_tag(tag_name)
		except (TypeError, IndexError):
			return default_value
	
	def get_attribute(self, attribute_name: str) -> str:
		if self.attrs is not None and isinstance(self.attrs, dict):
			for attr in self.attrs:
				if attr is not None and attr == attribute_name:
					return attr
		
		raise IndexError("Cannot find \'{}\' as attribute.".format(attribute_name))
	
	def get_attribute_or_default(self, attribute_name: str, default_value: object = None):
		try:
			return self.get_attribute(attribute_name)
		except IndexError:
			return default_value
	
	# OVERRIDES #
	
	def __getitem__(self, key):
		"""
		Try to find first a tag with a name equals to 'key', and if none has been found, try to find an attribute with
		this name.
		:param key: The name of the tag, or the attribute to get
		:return: Return another Element, or a string
		"""
		if isinstance(self.content, Element):
			return self.content[key]
		elif isinstance(self.content, list):
			try:
				return self.get_tag(key)
			except (TypeError, IndexError):
				pass
			
			# If no tag found, try to find an attribute in this instance
			try:
				return self.get_attribute(key)
			except IndexError:
				pass
			
			# Try another go
			if key == "content":
				return self.content
		elif key == "content":
			return self.content
		
		# Finally, raise an exception
		raise IndexError("Cannot find \'{}\' as tag or attribute.".format(key))
	
	def __call__(self, key, *args, **kwargs):
		"""
		Try to find first an attribute with a name equals to 'key', and if none has been found, try to find a tag with
		this name.
		:param key: The name of the attribute, or the tag to get
		:return: Return a string, or an Element
		"""
		try:
			return self.get_attribute(key)
		except IndexError:
			pass
		
		# If no tag found, try to find a tag in this instance
		try:
			return self.get_tag(key)
		except (TypeError, IndexError):
			pass
		
		try:
			if isinstance(self.content, Element):
				return self.content[key]
		except AttributeError:
			pass
		
		# Finally, raise an exception
		raise IndexError("Cannot find \'{}\' as attribute or tag.".format(key))