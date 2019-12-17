import unittest
from dotenv import load_dotenv
from source.custom_errs import AccessViolation
from source.websearch import Websearch
from source.client import  load_environment

environment_vars = load_environment()

class test_websearch(unittest.TestCase):

    mock_obj = Websearch(developerKey = environment_vars['GOOGLE_API_KEY'],
                            customsearch_id = environment_vars['GOOGLE_CSE_ID'])
    
    def test_instantiation(self):
        self.assertIsInstance(test_websearch.mock_obj, Websearch)

    @unittest.expectedFailure
    def test_private_developer_key(self):
        self.assertRaises(custom_errs.AccessViolation, 
            test_websearch.mock_obj.developerKey)


    def test_search_feature(self):
        res = test_websearch.mock_obj.search('google')
        self.assertIsNotNone(res)