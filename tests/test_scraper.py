import unittest
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from source.scraper import Scraper
from source.client import load_environment
from source.menu import Menu

environment_vars = load_environment()

class test_scraper(unittest.TestCase):

	instance = Scraper(environment_vars['LUNCH_MENU_URL'])

	def test_cache_is_none(self):
		self.assertIsNone(test_scraper.instance.cache)
	
	def test_url(self):
		self.assertIn('http', test_scraper.instance.url)

	def test_response(self):
		self.assertIsInstance(test_scraper.instance.response, bytes)

	def test_soup(self):
		self.assertIsInstance(test_scraper.instance.soup, BeautifulSoup)

	def test_get(self):
		self.assertIsInstance(test_scraper.instance.get(), Menu)
		self.assertIsNotNone(test_scraper.instance.cache)