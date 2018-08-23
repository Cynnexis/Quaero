# -*- coding: utf-8 -*-


class KeywordsError(Exception):
	
	def __init__(self, message: str):
		super(KeywordsError, self).__init__(message)
