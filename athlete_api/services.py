from sqlmodel import create_engine

from .config import config


#use db folder files for refactoring well: done
def connect(filename:str ='./database.ini',
            section:str='postgresql',
            echo:bool = False):
    params = config(filename=filename, section=section)
    DATABASE_URL = (f"postgresql://{params['user']}:{params['password']}"
                    f"@{params['host']}:{params['port']}"
                    f"/{params['database']}")
    #to stop multiple threads and concurrency lock
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, echo=echo)
    return engine
