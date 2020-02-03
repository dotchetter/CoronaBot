import praw
import source.commandintegrator.framework as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.redditjoke import RedditJoke


class RedditJokeFeatureCommandParser(fw.FeatureCommandParserBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RedditJokeFeature(fw.FeatureBase):

    FEATURE_KEYWORDS = (
        'skämt', 'meme',
        'skoja', 'skoj',
        'humor', 'roligt',
        'skämta'
    )

    FEATURE_SUBCATEGORIES = {
        'meme': CommandSubcategory.TELL_JOKE,
        'skämt': CommandSubcategory.TELL_JOKE,
        'skämta': CommandSubcategory.TELL_JOKE,
        'skoja': CommandSubcategory.TELL_JOKE,
        'skoj': CommandSubcategory.TELL_JOKE,
        'humor': CommandSubcategory.TELL_JOKE,
        'roligt': CommandSubcategory.TELL_JOKE
    }

    def __init__(self, *args, **kwargs):
        self.command_parser = RedditJokeFeatureCommandParser(
            category = CommandCategory.TELL_JOKE,
            keywords = RedditJokeFeature.FEATURE_KEYWORDS,
            subcategories = RedditJokeFeature.FEATURE_SUBCATEGORIES
        )

        self.command_mapping = {
            CommandSubcategory.TELL_JOKE: lambda: self.interface.get()
        }
        
        self.mapped_pronouns = (
            CommandPronoun.INTERROGATIVE,
        )

        super().__init__(
            command_parser = self.command_parser,
            command_mapping = self.command_mapping,
            interface = RedditJoke(reddit_client = praw.Reddit(**kwargs))
        )