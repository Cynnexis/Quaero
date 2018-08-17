import numpy as np
from unittest import TestCase
from typing import Union, Optional, List, Dict, Tuple, Set, Iterable, Any

from PIL import Image

from qr.info import Info
from qr.webengine import WebEngine
from qr.webresult import WebResult


class TestInfo(TestCase):
	
	def setUp(self):
		self.data1 = [["My title", "My content", 25], ["Title again", "Content again", 48]]
		
		self.dtype1a = List[List[Union[str, int]]]
		self.dtype1b = list
		self.dtype1c = type(self.data1)
		self.dtype1d = None
		
		self.dtype1 = (self.dtype1a, self.dtype1b, self.dtype1c, self.dtype1d)
		
		i = Info(data=self.data1)
		for dtype1 in self.dtype1:
			self.info1 = Info(data=self.data1, dtype=dtype1)
			self.assertEqual(i, self.info1)
		del i
		
		self.data = [self.data1]
		self.dtype = [self.dtype1]
		self.map = zip(self.data, self.dtype)
		self.info = [self.info1]
	
	def test_process(self):
		info1processed = Info([
			Info([
				Info("My title"),
				Info("My content"),
				Info(25)
			]),
			Info([
				Info("Title again"),
				Info("Content again"),
				Info(48)
			])
		], process_data=False)
		test_info1 = self.info1.process(update_attr=False)
		self.assertEqual(info1processed, test_info1)
		self.assertEqual(test_info1, self.info1.process())
		self.assertEqual(self.info1, self.info1.process())
	
	def test_autodetect_dtype(self):
		i = Info()
		# Simple type
		self.assertEqual(str, i.autodetect_dtype(""))
		self.assertEqual(int, i.autodetect_dtype(15))
		self.assertEqual(float, i.autodetect_dtype(7.2))
		self.assertEqual(complex, i.autodetect_dtype(7.2j + 5))
		self.assertEqual(Image.Image, i.autodetect_dtype(Image.Image()))
		
		# Object type
		self.assertNotEqual(list, i.autodetect_dtype([5.2]))
		self.assertNotEqual(tuple, i.autodetect_dtype((5.2,)))
		self.assertNotEqual(set, i.autodetect_dtype({5.2}))
		self.assertNotEqual(dict, i.autodetect_dtype({5.2: "test"}))
		
		self.assertEqual(List[float], i.autodetect_dtype([5.2]))
		self.assertEqual(List[Union[float, int, complex, str]], i.autodetect_dtype([5.2, 6, 4j + 2, ""]))
		self.assertEqual(List[None], i.autodetect_dtype([]))
		
		self.assertEqual(Tuple[float], i.autodetect_dtype((5.2,)))
		self.assertEqual(Tuple[Union[float, int, complex, str]], i.autodetect_dtype((5.2, 6, 4j + 2, "")))
		self.assertEqual(Tuple[None], i.autodetect_dtype(tuple()))
		
		self.assertEqual(Set[float], i.autodetect_dtype({5.2}))
		self.assertEqual(Set[Union[float, int, complex, str]], i.autodetect_dtype({5.2, 6, 4j + 2, ""}))
		self.assertEqual(Set[None], i.autodetect_dtype(set()))
		
		self.assertEqual(Dict[float, str], i.autodetect_dtype({5.2: "test"}))
		self.assertEqual(Dict[Union[float, int, complex, str], str], i.autodetect_dtype({5.2: "test", 6: "t", 4j + 2: "e", "string": "s"}))
		self.assertEqual(Dict[None, None], i.autodetect_dtype({}))
		
		self.assertEqual(np.ndarray, i.autodetect_dtype(np.array([5, 5, 9])))
	
	def test_check_data_against_dtype(self):
		i = Info()
		for k, v in self.map:
			self.assertTrue(i.check_data_against_dtype(k, v))
		
		for info in self.info:
			self.assertTrue(info.check_data_against_dtype())
		
		self.assertFalse(i.check_data_against_dtype("", int))
		self.assertFalse(i.check_data_against_dtype("", float))
		self.assertFalse(i.check_data_against_dtype("", complex))
		self.assertFalse(i.check_data_against_dtype("", List[int]))
		self.assertFalse(i.check_data_against_dtype("", List[str]))
		self.assertFalse(i.check_data_against_dtype("", Dict[str, str]))
		self.assertFalse(i.check_data_against_dtype("", Tuple[str]))
		self.assertFalse(i.check_data_against_dtype("", Set[str]))
	
	def test_assess_data_against_dtype(self):
		"""
		.. note:: copy/paste of test_check_data_against_dtype
		"""
		i = Info()
		for k, v in self.map:
			self.assertTrue(i.check_data_against_dtype(k, v))
		
		for info in self.info:
			self.assertTrue(info.check_data_against_dtype())
		
		self.assertRaises(TypeError, i.check_data_against_dtype("", int))
		self.assertRaises(TypeError, i.check_data_against_dtype("", float))
		self.assertRaises(TypeError, i.check_data_against_dtype("", complex))
		self.assertRaises(TypeError, i.check_data_against_dtype("", List[int]))
		self.assertRaises(TypeError, i.check_data_against_dtype("", List[str]))
		self.assertRaises(TypeError, i.check_data_against_dtype("", Dict[str, str]))
		self.assertRaises(TypeError, i.check_data_against_dtype("", Tuple[str]))
		self.assertRaises(TypeError, i.check_data_against_dtype("", Set[str]))
	
	def test_is_valid_dtype(self):
		i = Info()
		
		# TRUE
		self.assertTrue(i.is_valid_dtype(None))
		self.assertTrue(i.is_valid_dtype(int))
		self.assertTrue(i.is_valid_dtype(float))
		self.assertTrue(i.is_valid_dtype(complex))
		self.assertTrue(i.is_valid_dtype(str))
		self.assertTrue(i.is_valid_dtype(Image.Image))
		self.assertTrue(i.is_valid_dtype(Info))
		self.assertTrue(i.is_valid_dtype(np.ndarray))
		
		self.assertTrue(i.is_valid_dtype(List[int]))
		self.assertTrue(i.is_valid_dtype(List[float]))
		self.assertTrue(i.is_valid_dtype(List[complex]))
		self.assertTrue(i.is_valid_dtype(List[str]))
		self.assertTrue(i.is_valid_dtype(List[Image.Image]))
		self.assertTrue(i.is_valid_dtype(List[Info]))
		self.assertTrue(i.is_valid_dtype(List[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Tuple[int]))
		self.assertTrue(i.is_valid_dtype(Tuple[float]))
		self.assertTrue(i.is_valid_dtype(Tuple[complex]))
		self.assertTrue(i.is_valid_dtype(Tuple[str]))
		self.assertTrue(i.is_valid_dtype(Tuple[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Tuple[Info]))
		self.assertTrue(i.is_valid_dtype(Tuple[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Set[int]))
		self.assertTrue(i.is_valid_dtype(Set[float]))
		self.assertTrue(i.is_valid_dtype(Set[complex]))
		self.assertTrue(i.is_valid_dtype(Set[str]))
		self.assertTrue(i.is_valid_dtype(Set[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Set[Info]))
		self.assertTrue(i.is_valid_dtype(Set[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Dict[int, float]))
		self.assertTrue(i.is_valid_dtype(Dict[float, Image.Image]))
		self.assertTrue(i.is_valid_dtype(Dict[complex, int]))
		self.assertTrue(i.is_valid_dtype(Dict[str, Info]))
		self.assertTrue(i.is_valid_dtype(Dict[Image.Image, complex]))
		self.assertTrue(i.is_valid_dtype(Dict[Info, float]))
		self.assertTrue(i.is_valid_dtype(Dict[np.ndarray, int]))
		
		self.assertTrue(i.is_valid_dtype(Iterable[int]))
		self.assertTrue(i.is_valid_dtype(Iterable[float]))
		self.assertTrue(i.is_valid_dtype(Iterable[complex]))
		self.assertTrue(i.is_valid_dtype(Iterable[str]))
		self.assertTrue(i.is_valid_dtype(Iterable[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Iterable[Info]))
		self.assertTrue(i.is_valid_dtype(Iterable[np.ndarray]))
		
		# FALSE
		self.assertFalse(i.is_valid_dtype(WebResult))
		self.assertFalse(i.is_valid_dtype(WebEngine))
		self.assertFalse(i.is_valid_dtype(Union[WebEngine, WebResult]))
		self.assertFalse(i.is_valid_dtype(Union[WebEngine, int]))
	
	def test_assess_dtype(self):
		"""
		.. note:: copy/paste of test_is_valid_dtype
		"""
		i = Info()
		
		# TRUE
		self.assertTrue(i.is_valid_dtype(None))
		self.assertTrue(i.is_valid_dtype(int))
		self.assertTrue(i.is_valid_dtype(float))
		self.assertTrue(i.is_valid_dtype(complex))
		self.assertTrue(i.is_valid_dtype(str))
		self.assertTrue(i.is_valid_dtype(Image.Image))
		self.assertTrue(i.is_valid_dtype(Info))
		self.assertTrue(i.is_valid_dtype(np.ndarray))
		
		self.assertTrue(i.is_valid_dtype(List[int]))
		self.assertTrue(i.is_valid_dtype(List[float]))
		self.assertTrue(i.is_valid_dtype(List[complex]))
		self.assertTrue(i.is_valid_dtype(List[str]))
		self.assertTrue(i.is_valid_dtype(List[Image.Image]))
		self.assertTrue(i.is_valid_dtype(List[Info]))
		self.assertTrue(i.is_valid_dtype(List[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Tuple[int]))
		self.assertTrue(i.is_valid_dtype(Tuple[float]))
		self.assertTrue(i.is_valid_dtype(Tuple[complex]))
		self.assertTrue(i.is_valid_dtype(Tuple[str]))
		self.assertTrue(i.is_valid_dtype(Tuple[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Tuple[Info]))
		self.assertTrue(i.is_valid_dtype(Tuple[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Set[int]))
		self.assertTrue(i.is_valid_dtype(Set[float]))
		self.assertTrue(i.is_valid_dtype(Set[complex]))
		self.assertTrue(i.is_valid_dtype(Set[str]))
		self.assertTrue(i.is_valid_dtype(Set[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Set[Info]))
		self.assertTrue(i.is_valid_dtype(Set[np.ndarray]))
		
		self.assertTrue(i.is_valid_dtype(Dict[int, float]))
		self.assertTrue(i.is_valid_dtype(Dict[float, Image.Image]))
		self.assertTrue(i.is_valid_dtype(Dict[complex, int]))
		self.assertTrue(i.is_valid_dtype(Dict[str, Info]))
		self.assertTrue(i.is_valid_dtype(Dict[Image.Image, complex]))
		self.assertTrue(i.is_valid_dtype(Dict[Info, float]))
		self.assertTrue(i.is_valid_dtype(Dict[np.ndarray, int]))
		
		self.assertTrue(i.is_valid_dtype(Iterable[int]))
		self.assertTrue(i.is_valid_dtype(Iterable[float]))
		self.assertTrue(i.is_valid_dtype(Iterable[complex]))
		self.assertTrue(i.is_valid_dtype(Iterable[str]))
		self.assertTrue(i.is_valid_dtype(Iterable[Image.Image]))
		self.assertTrue(i.is_valid_dtype(Iterable[Info]))
		self.assertTrue(i.is_valid_dtype(Iterable[np.ndarray]))
		
		# FALSE
		self.assertRaises(TypeError, i.is_valid_dtype(WebResult))
		self.assertRaises(TypeError, i.is_valid_dtype(WebEngine))
		self.assertRaises(TypeError, i.is_valid_dtype(Union[WebEngine, WebResult]))
		self.assertRaises(TypeError, i.is_valid_dtype(Union[WebEngine, int]))
