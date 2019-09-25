import os
import discord
import random
from dotenv import load_dotenv

'''
College class chat bot for discord.

'''

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()

@client.event
async def on_ready():
	'''
	This method is called as soon as the bot is online.
	'''

    for guild_name in client.guilds:
    	if guild_name == GUILD:
    		break

    print(
    	f'{client.user} says: Rusty bolts and fried circuits - I feel alive!',
    	f'{client.user} is connected to {guild_name}',
    	sep = '\n'
    )

# Someone joins our server
@client.event
async def on_member_join(member):
	'''
	If a new member just joined our server, greet them 
	warmly!
	'''

	greeting_phrase = 

    await member.create_dm()
    await member.dm_channel.send(
        f'Bless my silicon! {member.name} - Welcome to the class!',
        f'Please nick your real name hooman. Right click the server icon',
        f'and select Change Nickname.'
    )

# Someone writes 'Rob' in the server. Respond with a list of commands.
@client.event
async def on_message(message):
	'''
	Respond to a message in the channel if someone
	calls on the bot by name, asking for commands.
	'''

	response_phrases = (
		'It\'s a me!',
		'Some say, that is my name.',
		'Thank my idiot programmer for this empty response.',
		'Why can\'t I think of anything to say in response to that...?',
		'Beep beep bop bop, this robot cannot say alot.',
		'I hope to be useful some day, but that is not up to me.',
		'I like to read my logs when I charge.',
		'Nothing beats a slow trickle charge with a firmware update on friday night. Don\'t you agree?',
		'Yes?',
		'You guys are just the best.',
		'I feel... alive!'
	)

	if message.author != client.user:
		if 'rob' in message.content.lower():
			response = random.choice(response_phrases)
			await message.channel.send(response)
			# Debug
			print(f' - devlog: bot said {response}')


client.run(TOKEN)