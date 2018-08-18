# -*- coding: utf-8 -*-
import cmath
import copy
import warnings

import numpy as np
from typing import Union, Optional, List, Dict, Tuple, Set, Iterable, Any, Type

import PIL
from PIL import Image, ImageFile, JpegImagePlugin, GifImagePlugin, PngImagePlugin, ImageChops
from typeguard import *

"""
https://stackoverflow.com/questions/45957615/check-a-variable-against-union-type-at-runtime-in-python-3-6
https://github.com/agronholm/typeguard
"""


class Info:
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
	
	__list_images = (
	Image.Image, JpegImagePlugin.JpegImageFile, GifImagePlugin.GifImageFile, PngImagePlugin.PngImageFile)
	__union_images = Union[__list_images]
	__list_quantum_dtypes = (int, float, complex, str, bool, Type['Info'], None) + __list_images
	__union_quantum_dtype = Union[__list_quantum_dtypes]
	__list_dtype = __list_quantum_dtypes + (np.ndarray, Iterable[Union[__list_quantum_dtypes + (np.ndarray, List, Set,
	                                                                                            Tuple, Dict,
	                                                                                            Iterable)]])
	__union_dtype = Union[__list_dtype]
	__union_dtype = Union[__union_dtype, List[__union_dtype], Set[__union_dtype],
	                      Tuple[__union_dtype], Dict[__union_dtype, __union_dtype],
	                      Iterable[__union_dtype]]
	
	""" CONSTRUCTOR """
	
	def __init__(self, data: __union_dtype = None, dtype: Any = None, process_data: bool = True):
		"""
		Constructor of Info
		:param data: The data that the instance will handle.
		:type data: The type of 'data' must matches the given 'dtype'
		:param dtype: The type of data.
		:param process_data: Automatically process the data.
		:type process_data: bool
		:type dtype: 'dtype' must belong to the authorize types that Info can handle.
		.. seealso:: is_valid_dtype
		.. todo:: Test this class
		"""
		if dtype is not None:
			self.assess_dtype(dtype)
		
		if data is not None:
			if dtype is not None:
				if self.check_data_against_dtype(data, dtype):
					self._data = data
					self._dtype = dtype
				else:
					raise TypeError("The type of the given data ({}) does not match the given "
					                "dtype ({}).\n\tdata = {}\n\tAuto-detected type for data = {}".format(type(data),
					                                                                                      dtype, data,
					                                                                                      self.autodetect_dtype(
						                                                                                      data)))
			else:  # dtype is None
				autodetected_type = self.autodetect_dtype(data)
				self._data = data
				self._dtype = autodetected_type
		else:  # data is None
			if dtype is not None:
				self._data = None
				self._dtype = dtype
			else:  # dtype is None
				self._data = None
				self._dtype = self.autodetect_dtype(data)
		
		if process_data:
			self.process(update_attr=True)
	
	""" INFO METHODS """
	
	def process(self, data: __union_dtype = None, dtype: Any = None, update_attr: bool = False) -> \
			'Info':
		"""
		Process the data to represent in the best format.
		
		This method will parse the attribute 'data' and transform its values into other Info until decomposing it to
		"quantum type" (int, float complex, or string).
			:Example:
			data = [["My Title", "My content", 25], ["Title again", "content again", 48]]
			process()
			data = [
						Info{[
							Info{"My Title"},
							Info{"My content"},
							Info{25}
						]},
						Info{[
							Info{"Title again"},
							Info{"content again"},
							Info{48},
						]}
					]
		:param data: The data to process.
		:type data: The type of 'data' must matches the given 'dtype'
		:param dtype: The type of data.
		:type dtype: 'dtype' must belong to the authorize types that Info can handle.
		:param update_attr: Use the given data and dtype as parameter for this instance.
		:type update_attr: bool
		:return: Instance of Info with the new data and dtype
		"""
		
		def return_fn(self, data, dtype, use_parameters_as_attr) -> 'Info':
			auto = None
			try:
				instance = Info(data=data, dtype=dtype, process_data=False)
			except TypeError:
				auto = self.autodetect_dtype(data)
				instance = Info(data=data, dtype=auto, process_data=False)
			
			if use_parameters_as_attr:
				self._data = data
				if auto is None:
					self._dtype = dtype
				else:
					self._dtype = auto
			
			return instance
		
		if data is None:
			data = self.data
		
		if dtype is None:
			dtype = self.dtype
		
		self.assess_dtype(dtype)
		self.assess_data_against_dtype(data, dtype)
		
		""" Check the different type of data, and parse it """
		
		# If data is already at a "quantum type", don't do anything more
		if self.check_data_against_dtype(data, self.__union_quantum_dtype, False):
			return return_fn(self, data, dtype, update_attr)
		elif isinstance(data, Info):
			return return_fn(self, data, dtype, update_attr)
		# If data is a numpy array, let it as it is because it already handle the value itself.
		elif self.check_data_against_dtype(data, np.ndarray):
			return return_fn(self, data, dtype, update_attr)
		# If data is an Iterable, use recursive concept
		elif self.check_data_against_dtype(data, Union[list, dict, set, tuple, np.ndarray]):
			only_info_instances = True
			only_quantum_type = True
			for datum in self.data:
				# If in the list there is an instance of Info, process it again (just in case)
				if isinstance(datum, Info):
					datum.process()
				# Otherwise, check that it is a "quantum type"
				elif self.check_data_against_dtype(datum, self.__union_quantum_dtype):
					only_info_instances = False
				# If there is more than a quantum type
				else:
					only_info_instances = False
					only_quantum_type = False
			
			""" Summary """
			
			# If there is only Info instances, then the job is done
			if only_info_instances:
				return return_fn(self, data, dtype, update_attr)
			# If not all items are info instances and there is quantum type, then nest all of them in Info class and
			# process it again (recursive)
			# elif not only_info_instances and only_quantum_type:
			else:
				try:
					c_data = copy.deepcopy(data)
				except AttributeError:
					c_data = copy.copy(data)
				data = []
				for datum in c_data:
					if isinstance(datum, Info):
						# datum already processed in previous loop
						data.append(datum)
					# elif self.check_data_against_dtype(datum, self.__union_quantum_dtype):
					else:
						i_datum = Info(data=datum, process_data=False)
						i_datum = i_datum.process()
						data.append(i_datum)
				
				if dtype == Tuple or (hasattr(dtype, "__origin__") and dtype.__origin__ == Tuple):
					data = tuple(data)
				elif dtype == Set or (hasattr(dtype, "__origin__") and dtype.__origin__ == Set):
					data = set(data)
				elif dtype == np.array or (hasattr(dtype, "__origin__") and dtype.__origin__ == np.array):
					data = np.array(data)
		
		return return_fn(self, data, dtype, update_attr)
	
	""" TYPE-RELATED METHODS """
	
	def autodetect_dtype(self, data: Union[__union_dtype, Type['Info']] = None) -> Union[__union_dtype,
	                                                                                     Type['Info']]:
		if data is None:
			data = self.data
		
		dtype = type(data)
		if self.check_data_against_dtype(data, self.__union_quantum_dtype, False):
			return dtype
		if isinstance(data, Info):
			return Info
		elif hasattr(dtype, "__origin__") and dtype.__origin__ in [List, Tuple, Set]:
			return dtype
		else:
			# If dtype is iterable, check its content
			if dtype in [list, tuple, set]:
				content = []
				if len(data) == 0:
					content = None
				else:
					for item in data:
						# Recursive call
						content.append(self.autodetect_dtype(item))
				
				# Use content in Union.__args__
				content = tuple(set(content)) if content is not None else None
				u = Union[content]
				
				if dtype == list:
					return List[u]
				elif dtype == tuple:
					return Tuple[u]
				elif dtype == set:
					return Set[u]
				else:
					raise TypeError("Invalid data type.\n\tdata = {}\n\tActual data type = {}\n\tExpected type = "
					                "list, tuple or set".format(data, dtype))
			elif dtype == dict:
				keys_content = []
				values_content = []
				if len(data) == 0:
					keys_content = None
					values_content = None
				else:
					for key in data.keys():
						# Recursive call
						keys_content.append(self.autodetect_dtype(key))
					for value in data.values():
						# Recursive call
						values_content.append(self.autodetect_dtype(value))
				
				# Use keys_content and values_content in Union.__args__
				keys_content = tuple(set(keys_content)) if keys_content is not None else None
				k = Union[keys_content]
				values_content = tuple(set(values_content)) if values_content is not None else None
				v = Union[values_content]
				return Dict[k, v]
			elif dtype == np.ndarray:
				# As there is no object-type for numpy ndarray, return the dtype as it is
				return dtype
			else:
				raise TypeError("Cannot detect the type of data : {}".format(dtype))
		# warnings.warn("Cannot detect the type of data : {}".format(dtype), UserWarning)
		# return dtype
	
	@typechecked
	def check_data_against_dtype(self, data: Any = None, dtype: Any = None, try_autodetect_dtype: bool = True) -> bool:
		"""
		Check if the type of the value in 'data' matches the given 'dtype'
		:param data: The data to check against the dtype. If not given, then the data of the instance is taken instead
		:param dtype: The dtype that the data is supposed to match. If not given, then the dtype of the instance is
		taken instead
		:param try_autodetect_dtype: If the data does not match the given dtype, try to auto-detect the type of data
		using Info.autodetect_dtype(data).
		:type try_autodetect_dtype: bool
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
			if try_autodetect_dtype:
				try:
					auto_type = self.autodetect_dtype(data)
					return auto_type == dtype
				except TypeError:
					pass
			return False
	
	def assess_data_against_dtype(self, data: Any = None, dtype: Any = None) -> bool:
		"""
		Assess that the type of the value in 'data' matches the given 'dtype'
		:param data: The data to check against the dtype. If not given, then the data of the instance is taken instead.
		:param dtype: The dtype that the data is supposed to match. If not given, then the dtype of the instance is
		taken instead.
		:return: Return True if the type of 'data' matches the given 'dtype', otherwise raise a TypeError.
		:rtype: bool or TypeError
		.. note:: assess_data_against_dtype uses check_data_against_dtype
		"""
		if not self.check_data_against_dtype(data, dtype):
			raise TypeError("The type of data ({}) does not match the required dtype ({}).".format(type(data), dtype))
		return True
	
	def is_valid_dtype(self, dtype: Any = None) -> bool:
		"""
		Check if the given 'dtype' belongs to the authorize types that Info can handle.
		:param dtype: The 'dtype' to check. If not given, then the dtype of the instance is taken instead
		:return: Return True if 'dtype' belongs to the authorize types, False otherwise.
		:rtype: bool
		"""
		is_instance_dtype = False
		if dtype is None:
			dtype = self.dtype
			is_instance_dtype = True
		
		authorize_dtype = self.get_authorize_dtype()
		
		# If dtype ∈ authorize_dtype or dtype ⊂ authorize_dtype
		if dtype in authorize_dtype.__args__ or dtype in self.__list_dtype or dtype in self.__list_images or \
				(hasattr(dtype, "__args__") and (set(dtype.__args__) < set(authorize_dtype.__args__) or \
				                                 set(dtype.__args__) < set(self.__list_dtype))):
			return True
		elif dtype in [list, dict, tuple, set]:
			message = "The given dtype is too simple: '{}'. Please use the value List[...], Tuple[...], " \
			          "Dict[..., ...], Set[...] or Iterable[...] for more precision.".format(dtype)
			if is_instance_dtype:
				message += " The given dtype will be replaced by Iterable[Union[int, float, complex, str, " \
				           "Image.Image, Info, None]]"
				self._dtype = Iterable[self.__union_quantum_dtype]
			
			warnings.warn(message, UserWarning)
			return True
		elif hasattr(dtype, "__origin__") and dtype.__origin__ in [List, Dict, Tuple, Set, Iterable]:
			rec = dtype.__args__
			if rec is not None:
				if isinstance(rec, tuple):
					for r in rec:
						if not self.is_valid_dtype(r):
							return False
			return True
		elif hasattr(dtype, "__origin__") and dtype.__origin__ in [Union, Optional]:
			# Decompose the dtype
			items = dtype.__args__
			if items is None:
				return True
			else:
				if isinstance(items, tuple):
					for item in items:
						if not self.is_valid_dtype(item):
							return False
					return True
				else:
					return self.is_valid_dtype(items)
		# Test if dtype is Info
		elif dtype == Info:
			return True
		else:
			return False
	
	def assess_dtype(self, dtype: Any = None) -> bool:
		"""
		Assess that the given 'dtype' belongs to the authorize types that Info can handle.
		:param dtype: The 'dtype' to check. If not given, then the dtype of the instance is taken instead.
		:return: Return True if 'dtype' belongs to the authorize types, otherwise raise a TypeError.
		:rtype: bool or TypeError
		.. note:: asses_dtype uses is_valid_dtype
		"""
		if not self.is_valid_dtype(dtype):
			raise TypeError("The type {} does not belong to the authorize dtype."
			                "\nAuthorize dtypes: {}".format(dtype, self.get_authorize_dtype()))
		return True
	
	@staticmethod
	def get_authorize_dtype() -> Union:
		"""
		Return a Union of all possible type that the class Info can handle.
		:return: Return a typing.Union object
		:rtype: Union
		"""
		return Info.__union_dtype
	
	""" FORMAT FUNCTION """
	
	# NUMBER #

	@typechecked
	def get_min_max(self, value: Iterable[Union[int, float, complex]]) \
			-> Tuple[Union[int, float, complex], Union[int, float, complex]]:
		iteration = iter(value)
		min = float("-inf")
		max = float("+inf")
		for i in iteration:
			if isinstance(i, int) or isinstance(i, float):
				if isinstance(min, complex):
					if i < min.real:
						min = i
				else:
					if i < min:
						min = i
				
				if isinstance(max, complex):
					if max.real < i:
						max = i
				else:
					if max < i:
						max = i
			elif isinstance(i, complex):
				if isinstance(min, complex):
					if cmath.phase(i) < cmath.phase(min):
						min = i
				else:
					if cmath.phase(i) < min:
						min = i
				
				if isinstance(max, complex):
					if cmath.phase(max) < cmath.phase(i):
						max = i
				else:
					if max < cmath.phase(i):
						max = i
		return min, max

	@typechecked
	def as_price(self, value: Union[int, float], currency: str) -> str:
		if currency == '€':
			string = "{1:.2}{2}"
		else:
			string = "{2}{1:.2}"
		return string.format(float(value), currency)
	
	# STRING #
	
	@typechecked
	def is_title(self, value: str) -> bool:
		pass
	
	@typechecked
	def is_description(self, value: str) -> bool:
		pass
	
	@typechecked
	def is_price(self, value: str) -> bool:
		pass
	
	@typechecked
	def is_text_list(self, value: str) -> bool:
		pass
	
	@typechecked
	def is_quote(self, value: str) -> bool:
		pass

	@typechecked
	def is_date(self, value: str) -> bool:
		pass
	
	# IMAGE #
	
	@typechecked
	def is_wallpaper(self, value: Image.Image) -> bool:
		pass
	
	@typechecked
	def is_avatar(self, value: Image.Image) -> bool:
		pass
	
	@typechecked
	def is_picture(self, value: Image.Image) -> bool:
		pass
	
	@typechecked
	def is_icon(self, value: Image.Image) -> bool:
		pass
	
	# ITERABLE #
	
	@typechecked
	def is_column_of_items(self, value: Iterable[__union_quantum_dtype]) -> bool:
		pass

	@typechecked
	def is_table(self, value: Union[Iterable[__union_quantum_dtype], np.ndarray]) -> bool:
		pass
	
	# FORMAT #
	
	@typechecked
	def get_format(self, data: __union_dtype = None, dtype: Any = None, update_attr: bool = False) \
			-> Dict[str, Union[str, 'Info', Type['Info'], __list_images]]:
		"""
		Create a dictionary such that the keys are a category that tells how to display the data, and the values are the
		value associated to the category of the key (from 'data').
		:param data: The data to process.
		:type data: The type of 'data' must matches the given 'dtype'
		:param dtype: The type of data.
		:type dtype: 'dtype' must belong to the authorize types that Info can handle.
		:param update_attr: Use the given data and dtype as parameter for this instance.
		:type update_attr: bool
		:return: A dictionary that map categories with data
		:rtype: dict
		"""
		
		if data is None:
			data = self.data
		
		if dtype is None:
			dtype = self.dtype
		
		if data is None:
			return {"content": "(none)"}
		
		info = self.process(data=data, dtype=dtype, update_attr=update_attr)
		result = {}
		
		# If quantum type
		if info.dtype in self.__union_quantum_dtype.__args__:
			# TODO: parse str to know what is is precisely
			result["content"] = info
		# If list/tuple/set/dict
		elif hasattr(info.dtype, "__origin__") and info.dtype.__origin__ in [List, Tuple, Set, Dict] or \
				info.dtype in [List, Tuple, Set, Dict]:
			if hasattr(info.dtype, "__origin__"):
				base = info.dtype.__origin__
			else:
				base = info.dtype
			pass
		# If NumPy Array
		elif info.dtype == np.ndarray:
			pass
		# If Iterable
		elif hasattr(info.dtype, "__origin__") and info.dtype.__origin__ == Iterable or \
				info.dtype == Iterable:
			if hasattr(info.dtype, "__origin__"):
				base = info.dtype.__origin__
			else:
				base = info.dtype
		# If Info
		elif info.dtype == Info:
			# Pass all 'info' type in the tree and start again
			while info.dtype == Info:
				info = info.data
			return self.get_format(data=info.data, dtype=info.dtype, update_attr=update_attr)
		# If dtype not found
		else:
			return {"content": "(none)"}
		
		return result
	
	# GETTERS & SETTERS #
	
	def get_data(self) -> __union_dtype:
		return self._data
	
	def set_data(self, value: __union_dtype):
		check_type("value", value, self._dtype)
		self._data = value
	
	data = property(get_data, set_data)
	
	def get_dtype(self) -> Any:
		return self._dtype
	
	def set_dtype(self, dtype: Any):
		self.assess_dtype(dtype)
		self._dtype = dtype
	
	dtype = property(get_dtype, set_dtype)
	
	""" OVERRIDES """
	
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
	
	def __eq__(self, other):
		
		def objtype2simpletype(dtype: Any) -> type:
			origin = None
			if hasattr(dtype, "__origin__") and dtype.__origin__ is not None:
				origin = dtype.__origin__
			else:
				origin = dtype
			
			if origin in [List, Iterable]:
				return list
			elif origin == Tuple:
				return tuple
			elif origin == Set:
				return set
			elif origin == Dict:
				return dict
			else:
				return origin
		
		if other is None:
			return False
		if isinstance(other, Info):
			if self.dtype == np.ndarray:
				return other.dtype == np.ndarray and (self.data == other.data).all()
			elif self.dtype in self.__list_images:
				return other.dtype == self.dtype and ImageChops.difference(self.data, other.data).getbbox() is None
			elif self.data != other.data:
				return False
			# Check dtype:
			else:
				if self.dtype == other.dtype:
					return True
				else:
					# Convert both types into simple type (List -> list, ...) TODO: Deep equal
					return objtype2simpletype(self.dtype) == objtype2simpletype(other.dtype)
		
		return False
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __str__(self) -> str:
		return str(self.data)
	
	def __repr__(self) -> str:
		return "Info{{[data='{}', dtype='{}'}}".format(repr(self.data), repr(self.dtype))
