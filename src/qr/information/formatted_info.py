# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Union, Any
from typeguard import *

from qr.information.info import Info


class FormattedInfo(ABC):
	
	def __init__(self, info_formatted: dict = None):
		if info_formatted is None:
			info_formatted = {}
		
		self._info_formatted = info_formatted
	
	@abstractmethod
	def get_format(self, output_type: type) -> Any:
		pass
	
	# GETTER & SETTER #
	
	def get_info_formatted(self) -> dict:
		return self._info_formatted
	
	@typechecked
	def set_info_formatted(self, info_formatted: dict):
		self._info_formatted = info_formatted
	
	info_formatted = property(get_info_formatted, set_info_formatted)
	
	# OVERRIDES #
	
	def __eq__(self, other):
		if other is None:
			return False
		
		if not isinstance(other, FormattedInfo):
			return False
		else:
			return self.info_formatted == other.info_formatted
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __str__(self):
		f = self.get_format()
		if isinstance(f, str):
			return f
		else:
			return self.__repr__()
	
	def __repr__(self):
		return "FormattedInfo{{info_formatted='{}'}}".format(self.info_formatted)
