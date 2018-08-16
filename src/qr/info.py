# -*- coding: utf-8 -*-
import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Optional, List, Dict, Tuple, Set, Iterable, Any

from PIL import Image
from typeguard import *

"""
https://stackoverflow.com/questions/45957615/check-a-variable-against-union-type-at-runtime-in-python-3-6
https://github.com/agronholm/typeguard
"""


class Info(ABC):
	"""
	Handle a data to display it as the best format.
	
	Take a data as parameter and, using its type, try to make the best representation of this data. The following list
	shows all the different forms that a data can have:
	- Text
	- Image (using Pillow module)
	- Number (integer, float, complex)
	- List (list/set/dict/tuple/numpy array) containing other instances of Info
	- Table (same as the item above) containing other instances of Info
	"""
	
	__authorize_dtype = Union[int, float, complex, str, Image.Image, np.ndarray, None, Iterable[Union[int, float, complex, str, Image.Image, np.ndarray, None]]]
	
	def __init__(self, data: __authorize_dtype = None, dtype: Any = None):
		"""
		Constructor of Info
		:param data: The data that the instance will handle.
		:type data: The type of 'data' must matches the given 'dtype'
		:param dtype: The type of data.
		:type dtype: 'dtype' must belong to the authorize types that Info can handle.
		.. seealso:: is_valid_dtype
		.. todo:: Test this class
		"""
		if dtype is not None:
			self.asses_dtype(dtype)
		
		if data is not None:
			if dtype is not None:
				if self.check_data_against_dtype(data, dtype):
					self._data = data
					self._dtype = dtype
				else:
					raise TypeError("The type of the given data ({}) does not match the given"
					                "dtype ({})".format(type(data), dtype))
			else: # dtype is None
				self.asses_dtype(type(data))
				self._data = data
				self._dtype = type(data)
		else: # data is None
			if dtype is not None:
				self._data = None
				self._dtype = dtype
			else: # dtype is None
				self._data = None
				self._dtype = type(None)
	
	# INFO METHODS #
	
	def process(self):
		"""
		Process the data to represent in the best format.
		:return: None
		"""
		pass
	
	def check_data_against_dtype(self, data: Any = None, dtype: Any = None) -> bool:
		"""
		Check if the type of the value in 'data' matches the given 'dtype'
		:param data: The data to check against the dtype. If not given, then the data of the instance is taken instead
		:param dtype: The dtype that the data is supposed to match. If not given, then the dtype of the instance is
		taken instead
		:return: Return True if the type of 'data' matches the given 'dtype', False otherwise.
		:rtype: bool
		"""
		if data is None:
			data = self.data
		
		if dtype is None:
			dtype = self.dtype
		
		try:
			check_type("data", data, dtype)
			return True
		except TypeError:
			return False
	
	def is_valid_dtype(self, dtype: Any = None) -> bool:
		"""
		Check if the given 'dtype' belongs to the authorize types that Info can handle.
		:param dtype: The 'dtype' to check. If not given, then the dtype of the instance is taken instead
		:return: Return True if 'dtype' belongs to the authorize types, False otherwise.
		:rtype: bool
		"""
		if dtype is None:
			dtype = self.dtype
		
		authorize_dtype = self.get_authorize_dtype()
		# If dtype ∈ authorize_dtype or dtype ⊂ authorize_dtype
		return dtype in authorize_dtype or (hasattr(dtype, "__args__") and set(dtype.__args__) < set(authorize_dtype.__args__))
	
	def asses_dtype(self, dtype: Any = None) -> bool:
		"""
		Assess that the given 'dtype' belongs to the authorize types that Info can handle.
		:param dtype: The 'dtype' to check. If not given, then the dtype of the instance is taken instead
		:return: Return True if 'dtype' belongs to the authorize types, otherwise raise a TypeError
		:rtype: bool or TypeError
		.. note:: asses_dtype uses is_valid_dtype
		"""
		if not self.is_valid_dtype(dtype):
			raise TypeError("The type {} does not belong to the authorize dtype."
			                "\nAuthorize dtypes: {}".format(dtype, self.get_authorize_dtype()))
		return True
	
	@staticmethod
	def get_authorize_dtype():
		"""
		Return a Union of all possible type that the class Info can handle.
		:return: Return a typing.Union object
		:rtype: Union
		"""
		return Info.__authorize_dtype
	
	# GETTERS & SETTERS #
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, value):
		check_type("value", value, self._dtype)
		self._data = value
	
	@property
	def dtype(self) -> Any:
		return self._dtype
	
	@dtype.setter
	def dtype(self, dtype: Any):
		self.asses_dtype(dtype)
		self._dtype = dtype
	
	# OVERRIDES #

	def __getitem__(self, key: Any) -> Any:
		try:
			check_type("data", self.data, Union[List, Dict, Tuple, Set, Iterable])
			return self.data[key]
		except TypeError:
			if key == 0:
				return self.data
			else:
				raise IndexError()
	
	def __setitem__(self, key: Any, value: Any) -> None:
		try:
			check_type("data", self.data, Union[List, Dict, Tuple, Set, Iterable])
			self.data[key] = value
		except TypeError:
			if key == 0:
				self.data = value
			else:
				raise IndexError()
	
	@abstractmethod
	def __str__(self) -> str:
		return str(self.data)
	
	def __repr__(self) -> str:
		return "Result{data='{}', dtype='{}'}".format(repr(self.data), repr(self.dtype))
