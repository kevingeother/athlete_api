"""
Engine creation function
"""

from sqlmodel import create_engine

from .config import config


def connect(filename:str,
            section:str,
            echo:bool = False):
  """Connection method

  Args:
      filename (str): filename of database.ini config to look for
      section (str): section in .ini file to look for
      echo (bool, optional): echo steps in engine. Defaults to False.

  Returns:
      engine: sqlmodel engine 
  """
  params = config(filename=filename, section=section)
  DATABASE_URL = (f"postgresql://{params['user']}:{params['password']}"
                  f"@{params['host']}:{params['port']}"
                  f"/{params['database']}")
  #to stop multiple threads and concurrency lock
  connect_args = {"check_same_thread": False}
  engine = create_engine(DATABASE_URL, echo=echo)
  return engine
