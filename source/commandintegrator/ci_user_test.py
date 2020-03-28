"""
This file contains code that can be used to test the CI
framework. The code here has been moved from the __init__ file
and is not changed since then in the current state.
"""

import argparse
import commandintegrator as ci

if __name__ == "__main__":

    enviromnent_strings = [
        'DISCORD_GUILD',
        'DISCORD_TOKEN',
        'CORONA_API_URI',
        'CORONA_API_RAPIDAPI_HOST',
        'CORONA_API_RAPIDAPI_KEY'
    ]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-testmode', action = 'store_true')
    args = arg_parser.parse_args()

    from source import client as client
    from features.CoronaSpreadFeature import CoronaSpreadFeature

    with open('commandintegrator.settings.json', 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())['default_responses']

    environment_vars = client.load_environment(enviromnent_strings)
    
    processor = CommandProcessor(
        pronoun_lookup_table = PronounLookupTable(), 
        default_responses = default_responses
    )
    
    processor.features = (
        
        ScheduleFeature(url = environment_vars['TIMEEDIT_URL']),
        
        CoronaSpreadFeature(
            CORONA_API_URI = environment_vars['CORONA_API_URI'],
            CORONA_API_RAPIDAPI_HOST = environment_vars['CORONA_API_RAPIDAPI_HOST'],
            CORONA_API_RAPIDAPI_KEY = environment_vars['CORONA_API_RAPIDAPI_KEY'],
            translation_file_path = ''
        ),

        LunchMenuFeature(
            url = environment_vars['LUNCH_MENU_URL']),
            RedditJokeFeature(
                client_id = environment_vars['REDDIT_CLIENT_ID'], 
                client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                user_agent = environment_vars['REDDIT_USER_AGENT']
            )
        )


    # --- FOR TESTING THE COMMANDINTEGRATOR FRAMEWORK, run the __init__ file with -testmode from terminal --- 

    mock_message = discord.Message

    if args.testmode:
        print(f'\n# Test mode initialized, running CommandIntegrator version: {VERSION}')
        print('# Features loaded: ', '\n')
        [print(f'  * {i}') for i in processor.features]
        print(f'\n# Write a message and press enter, as if you were using your app front end.')
        
        while True:
            mock_message.content = input('->')
            if not len(mock_message.content):
                continue

            before = timer()
            a = processor.process(mock_message)
            after = timer()

            print(f'Responded in {round(1000 * (after - before), 3)} milliseconds')

            if callable(a.response):
                print(f'\nINTERPRETATION:\n{a}\n\nEXECUTED RESPONSE METHOD: {a.response()}')
                if a.error:
                    print('Errors occured, see caught traceback below.')
                    pprint(a.error)
            else:
                print(f'was not callable: {a}')