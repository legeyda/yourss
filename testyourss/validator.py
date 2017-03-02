from unittest import TestCase

import yourss.valid as validator


class ValidatorTest(TestCase):
	def test_page_size(self):
		self.assertEqual(10, validator.PageSize(None).value())
		self.assertRaises(validator.ParameterException, validator.PageSize('blabla').value)
		self.assertRaises(validator.ParameterException, validator.PageSize(-1).value)
	def test_page_index(self):
		self.assertEqual(1, validator.PageIndex(None).value())
		self.assertRaises(validator.ParameterException, validator.PageIndex('blabla').value)
		self.assertRaises(validator.ParameterException, validator.PageIndex(-1).value)
	def test_quality(self):
		self.assertEqual('high', validator.Quality(None).value())
		self.assertEqual('high', validator.Quality('high').value())
		self.assertEqual('low', validator.Quality('low').value())
		self.assertRaises(validator.ParameterException, validator.Quality('blabla').value)






