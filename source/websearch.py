from apiclient.discovery import build
from custom_errs import AccessViolation
from random import choice
'''
Details:
    2019-11-24

Module details:
    Google Custom search handling class

Synposis:
	Provide a way for the chatbot to search
	the web for specific queries. The Custom
	search engine is setup to return responses
	from a defined set of domains, related to 
	computer science and programming in general.
'''

class Websearch:

	'''
	A web search response using Google Custom Search
	engine. The instance object will hold data of interest
	such as link and title.
	'''

	def __init__(self, *args, **kwargs):
		for key in kwargs:
			setattr(self, key, kwargs[key])

		self._service = build('customsearch', 'v1', 
			developerKey = self._developerKey).cse()

	def search(self, query):
		'''
		Return only the URL from a websearch, based upon query.
		If the search resulted in 0 matches, return None.
		'''
		prefixes = (
			'Jag hittade detta!',
			'Vad tror du om det där?',
			'Hittade detta på webben, vad sägs om det?',
			'Här har du lite läsning om det!',
			'Det finns många svar på det men.. jag tror det där passar.',
		)

		result = self._service.list(
					q = query, 
					safe = 'active',
					cx = self.customsearch_id, 
					num = 1).execute()
		
		if int(result['queries']['request'][0]['totalResults']) > 0:
			link = result['items'][0]['link']
			return f"{choice(prefixes)} :slight_smile:\n{link}"
		return None

	@property
	def developerKey(self):
		raise AccessViolation('Access denied')

	@developerKey.setter
	def developerKey(self, key):
		self._developerKey = key

	@property
	def customsearch_id(self):
		return self._customsearch_id

	@customsearch_id.setter
	def customsearch_id(self, csid):
		self._customsearch_id = csid