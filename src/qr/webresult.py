# -*- coding: utf-8 -*-
import urllib
from urllib import request
import requests
from io import BytesIO
from typing import Optional, Union
from typeguard import *
from PIL import Image

from qr.webutils import assess_url


class WebResult:
	"""
	Class that represents a result given by a web engine, such as google.
	"""
	
	@typechecked
	def __init__(self, title: Optional[str], url: Optional[str], thumbnail: Optional[Union[Image.Image, str]],
	             date: Optional[str], description: Optional[str]):
		self._title = title
		self._url = url
		self._thumbnail = thumbnail
		self._date = date
		self._description = description
		
		if self._thumbnail is not None and isinstance(self._thumbnail, str):
			#try:
			self.force_download_thumbnail(self._thumbnail)
			#except TypeError:
			#	pass
	
	# GETTERS & SETTERS #
	
	@property
	def title(self) -> Optional[str]:
		return self._title
	
	@title.setter
	@typechecked
	def title(self, value: Optional[str]):
		self._title = value
	
	@property
	def url(self) -> Optional[str]:
		return self._url
	
	@url.setter
	@typechecked
	def url(self, value: Optional[str]):
		self._url = value
	
	@property
	def thumbnail(self) -> Optional[Union[Image.Image, str]]:
		return self._thumbnail
	
	@thumbnail.setter
	@typechecked
	def thumbnail(self, value: Optional[Union[Image.Image, str]], download_if_url: bool = True):
		self._thumbnail = value
		if download_if_url:
			self._thumbnail = self.__get_image()
	
	@property
	def date(self) -> Optional[str]:
		return self._date
	
	@date.setter
	@typechecked
	def date(self, value: Optional[str]):
		self._date = value
	
	@property
	def description(self) -> Optional[str]:
		return self._description
	
	@description.setter
	@typechecked
	def description(self, value: Optional[str]):
		self._description = value

	@typechecked
	def force_download_thumbnail(self, url: str = None):
		img = self.__get_image(url)
		if isinstance(img, str):
			raise TypeError("Could not download the image using the url '{}'.".format(img))
		elif img is None:
			raise TypeError("Could not download the image using the url ''.".format(url if url is not None else self._thumbnail))
		else:
			self._thumbnail = img

	@typechecked
	def __get_image(self, url: str = None):
		if url is None:
			url = self._thumbnail
		
		if url is not None and isinstance(url, str) and assess_url(url):
			reponse = requests.get(self._thumbnail)
			return Image.open(BytesIO(reponse.content))
		
		return url
	
	# OVERRIDES #
	
	def __eq__(self, o: object) -> bool:
		return isinstance(o, WebResult) and self.title == o.title and self.url == o.url and self.date == o.date and \
				self.description == o.description
	
	def __str__(self) -> str:
		content = "WebResult{{" \
		          "title='{}'," \
		          "url='{}'," \
		          "thumbnail='{}'," \
		          "date='{}'," \
		          "description='{}'}}".format(self.title, self.url, self.thumbnail, self.date, self.description)
		return content
	
	def __repr__(self) -> str:
		string = "{}\n{}\n".format(self.title, self.url)
		if self._thumbnail is not None:
			if isinstance(self._thumbnail, str):
				string += "[Thumbnail URL: {}]\n".format(self._thumbnail)
			elif isinstance(self.thumbnail, Image.Image):
				string += "[Thumbnail Image: {}]\n".format(self._thumbnail)
			else:
				string += "[Thumbnail object: {}]\n".format(str(self._thumbnail))
		
		if self.date is not None and len(self.date) > 0:
			string += "{}".format(self.date)
		
		if self.description is not None and len(self.description) > 0:
			if self.date is not None and len(self.date) > 0:
				string += " - "
			
			string += "{}".format(self.description)
		
		return string

