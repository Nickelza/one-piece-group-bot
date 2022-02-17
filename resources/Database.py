import constants as const

from os import environ
from dotenv import load_dotenv
import sys
from peewee import *

load_dotenv(sys.argv[1])


class Database:
    def __init__(self):

        self.db = MySQLDatabase(environ[const.ENV_DB_NAME], host=environ[const.ENV_DB_HOST],
                                port=int(environ[const.ENV_DB_PORT]), user=environ[const.ENV_DB_USER],
                                password=environ[const.ENV_DB_PASSWORD])

    def get_db(self):
        if self.db.is_connection_usable():
            return self.db

        self.db.connect()
        return self.db

    def close(self):
        self.db.close()
