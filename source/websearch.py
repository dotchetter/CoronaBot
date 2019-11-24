from apiclient.discovery import build
from custom_errs import AccessViolation

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
		result = self._service.list(
					q = query, cx = self.customsearch_id, 
					safe = 'active',
					num = 1).execute()
		
		if int(result['queries']['request'][0]['totalResults']) > 0:
			return result['items'][0]['link']
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