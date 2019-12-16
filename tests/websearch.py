from source.custom_errs import AccessViolation
from source.websearch import Websearch
import unittest


class test_websearch(unittest.TestCase):
    
    @unittest.expectedFailure
    def test_private_developer_key(self):
        mock_obj = Websearch(developerKey = 'PRIVATE',
                            customsearch_id = 'PRIVATE')
    
        self.assertRaises(custom_errs.AccessViolation, mock_obj.developerKey)

