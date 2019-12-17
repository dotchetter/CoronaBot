from datetime import datetime
from source.unrecognizedcommand import UnrecognizedCommand
import unittest


class test_unrecognizedCommand(unittest.TestCase):

	def test_timestamp(self):
		mock_obj = UnrecognizedCommand(
			author = 'author', command = 'command')

		self.assertEqual(mock_obj.author, 'author')
		self.assertEqual(mock_obj.command, 'command')
		