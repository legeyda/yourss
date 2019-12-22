from unittest import TestCase

from yourss.asynch import StdoutRedirector
from sys import stdout


class ValidatorTest(TestCase):
	def test_redirector_works(self):
		example=['1', '2', '3']
		def producer():
			for s in example:
				stdout.write(s)
		bucket=[]
		for item in StdoutRedirector(producer, queue_size=100, timeout=60, check_interval=5):
			bucket.append(item)
		self.assertEqual(example, bucket)
		# fails, i suppose due to unittest also redirects stdout