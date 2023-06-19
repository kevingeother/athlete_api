"""
Config parser function
"""
from configparser import ConfigParser
import os


def config(filename:str, section:str):
    """
    Read config file and return db object. This function is used to read the config file for database creation

    Args:
      filename: Name of the config file
      section: Name of the section to read default to postgresql

    Returns: 
      Postgresql object with configuration parameters from the config file or empty if not found. 
    """
    # Read the config file and return a dictionary of parameters
    print(filename)
    # create a parser
    if os.path.isfile(filename):
        parser = ConfigParser()
        # read config file
        parser.read(filename)
        # get section, default to postgresql
        db = {}
        print(list(parser.items()))
        print(parser.sections())
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    else:
        raise Exception(f'Config file {filename} not found')
    return db
