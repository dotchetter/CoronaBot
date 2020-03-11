import praw
from random import randint

class RedditJoke:

    def __init__(self, reddit_client: praw.Reddit):
        self.reddit_client = reddit_client

    def get(self) -> str:
        """
        Return a random url or random joke phrase parsed
        from reddits api client 'praw'. Ensure that the returned
        joke is sub 2000 characters and randomize the choice between
        the two alternatives, r/jokes and r/programmerhumor
        """

        iterations = 0
        iteration_limit = 10

        while True:
            iterations += 1
            joke_selection = randint(0, 1)

            if joke_selection == 0:
                submission = self.reddit_client.subreddit('jokes').random()
                message = f'{submission.title}\n||{submission.selftext}||'
            else:
                submission = self.reddit_client.subreddit('ProgrammerHumor').random()
                message =  f'{submission.title}\n{submission.url}'
            
            if len(message) < 2000:
                break
            elif iterations == iteration_limit:
                message = f'Jag kommer inte på något... :cry:'
                break
        return message

    @property
    def reddit_client(self) -> praw.Reddit:
        return self._reddit_client

    @reddit_client.setter
    def reddit_client(self, client):
        self._reddit_client = client
