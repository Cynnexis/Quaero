# -*- coding: utf-8 -*-


class WebResult:
	
	def __init__(self, title: str, url: str, date: str, description: str):
		self._title = title
		self._url = url
		self._date = date
		self._description = description
	
	# GETTERS & SETTERS #
	
	@property
	def title(self):
		return self._title
	
	@title.setter
	def title(self, value):
		self._title = value
	
	@property
	def url(self):
		return self._url
	
	@url.setter
	def url(self, value):
		self._url = value
	
	@property
	def date(self):
		return self._date
	
	@date.setter
	def date(self, value):
		self._date = value
	
	@property
	def description(self):
		return self._description
	
	@description.setter
	def description(self, value):
		self._description = value
	
	# OVERRIDES #
	
	def __eq__(self, o: object) -> bool:
		return isinstance(o, WebResult) and self.title == o.title and self.url == o.url and self.date == o.date and \
				self.description == o.description
	
	def __str__(self) -> str:
		return self.__repr__()
	
	def __repr__(self) -> str:
		return "{}\n{}\n{} - {}".format(self.title, self.url, self.date, self.description)

