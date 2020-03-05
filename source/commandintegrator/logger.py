import os
import json
import logging
import functools
from pathlib import Path

"""
Module details:
    This module contains function(s) for logging
    the application methods during runtime. As of
    writing this description, there is one method
    called logger that provides this functionality.

"""

LOGFORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"

with open ('commandintegrator.settings.json', 'r', encoding = 'utf-8') as f:
    LOG_DIR = Path(json.loads(f.read())['log_dir'])

LOG_FILE = 'runtime.log'
LOG_FILE_FULLPATH = LOG_DIR / LOG_FILE

if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

logging.basicConfig(level = logging.DEBUG, 
                    filename = LOG_FILE_FULLPATH, 
                    format = LOGFORMAT)

def logger(func) -> 'class function':
    """
    Wrapper method for providing logging functionality.
    Use @logger to implement this method where logging
    of methods are desired.
    :param func:
        method that will be wrapped
    :returns:
        function
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        """
        Inner method, executing the func paramter function,
        as well as executing the logger.
        :param *args:
            arbitrary parameters for the wrapped function
        :param **kwargs:
            arbitrary keyword parameters for the wrapped function
        :returns:
            Output from executed function in parameter func
        """
        try:
            logging.debug(f'Ran {func.__name__} with args:{args} kwargs: {kwargs}')
            results = func(*args, **kwargs)
            logging.debug(f'Results: {results}')
            return results
        except Exception as e:
            logging.debug(f'Exception occured in {func.__name__}: {e}')
            raise e
        return results
    return inner


if __name__ == '__main__':
    
    @logger
    def test(a, b):
        return a + b

    @logger
    def fails(a, b):
        raise Exception('this is the error message')    

    print(test(1,2))