import discord
import os
import source.commandintegrator as fw
from source.commandintegrator.enumerators import CommandPronoun, CommandCategory, CommandSubcategory
from source.commandintegrator.logger import logger

class RankingMembersFeatureCommandParser(fw.FeatureCommandParserBase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class RankingMembersFeature(fw.FeatureBase):

	FEATURE_KEYWORDS = (
		'rank',
		'ranks'
	)

	rank_for_all = {'rank': ('alla', 'all')}
	rank_up = {'rank': ('upp', 'up')}
	rank_down = {'rank': ('ner', 'ned', 'down')}

	FEATURE_SUBCATEGORIES = {
		str(rank_for_all): CommandSubcategory.RANKING_FOR_ALL,
		str(rank_down): CommandSubcategory.RANKING_DOWN,
		str(rank_up): CommandSubcategory.RANKING_UP,
		'för': CommandSubcategory.RANKING_FOR_MEMBER,
		'for': CommandSubcategory.RANKING_FOR_MEMBER
	}

	def __init__(self, *args, **kwargs):
		self.command_parser = RankingMembersFeatureCommandParser(
			category = CommandCategory.RANKING,
			keywords = RankingMembersFeature.FEATURE_KEYWORDS,
			subcategories = RankingMembersFeature.FEATURE_SUBCATEGORIES
		)
		
		self.user_rankings = {}

		self.callbacks = {
			CommandSubcategory.RANKING_UP: self.rank_up,
			CommandSubcategory.RANKING_DOWN: self.rank_down,
			CommandSubcategory.RANKING_FOR_MEMBER: self.rank_for_member,
			CommandSubcategory.RANKING_FOR_ALL: lambda: self.rank_for_all()
		}

		self.mapped_pronouns = (
			CommandPronoun.UNIDENTIFIED,
		)

		self.interactive_methods = (
			self.rank_up, 
			self.rank_down,
			self.rank_for_member
		)
	
		super().__init__(
			command_parser = self.command_parser,
			callbacks = self.callbacks,
			interactive_methods = self.interactive_methods
		)

	@logger
	def rank_up(self, message: discord.Message) -> str:
		"""
		Rank up a user upon command
		"""
		output = []
		for member in message.mentions:
			try:
				self.user_rankings[member] += 1
			except KeyError:
				self.user_rankings[member] = 1
			output.append(f'{member.mention} ökade till: {self.user_rankings[member]}')
		return f'{os.linesep.join(output)}'

	@logger
	def rank_down(self, message: discord.Message) -> str:
		"""
		Rank down a user upon command
		"""
		output = []
		for member in message.mentions:
			try:
				self.user_rankings[member] -= 1
			except KeyError:
				self.user_rankings[member] = 1
			output.append(f'{member.mention} minskade till: {self.user_rankings[member]}')
		return f'{os.linesep.join(output)}'

	@logger
	def rank_for_member(self, message: discord.Message) -> str:
		"""
		Return the current rank for a member
		"""
		output = []
		for member in message.mentions:
			try:
				output.append(f'{member.mention} rankar: {self.user_rankings[member]}')
			except KeyError:
				output.append(f'{member.mention} har inte rankats')
		return f'{os.linesep.join(output)}'

	@logger
	def rank_for_all(self):
		"""
		Return ranks for all members in a list
		"""
		output = []
		for member in self.user_rankings:
			output.append(f'{member.mention} rankar: {self.user_rankings[member]}')
		return f'{os.linesep.join(output)}'