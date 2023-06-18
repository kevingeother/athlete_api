#!/usr/bin/python
from configparser import ConfigParser
import os

def config(filename='./database.ini', section='postgresql'):
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
