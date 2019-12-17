from source.custom_errs import AccessViolation
from source.websearch import Websearch
from source.client import  load_environment
from dotenv import load_dotenv
import unittest

environment_vars = load_environment()

class test_websearch(unittest.TestCase):
    
    def test_instantiation(self):
        mock_obj = Websearch(developerKey = environment_vars['GOOGLE_API_KEY'],
                            customsearch_id = environment_vars['GOOGLE_CSE_ID'])
        self.assertIsInstance(mock_obj, Websearch)

    @unittest.expectedFailure
    def test_private_developer_key(self):
        mock_obj = Websearch(developerKey = environment_vars['GOOGLE_API_KEY'],
                            customsearch_id = environment_vars['GOOGLE_CSE_ID'])
        self.assertRaises(custom_errs.AccessViolation, mock_obj.developerKey)


    def test_search_feature(self):
        mock_obj = Websearch(developerKey = environment_vars['GOOGLE_API_KEY'],
                            customsearch_id = environment_vars['GOOGLE_CSE_ID'])
        res = mock_obj.search('google')
        self.assertIsNotNone(res)