from abc import ABC

import constants as c

from os import environ
from dotenv import load_dotenv
import sys
from peewee import *
from playhouse.shortcuts import ReconnectMixin

load_dotenv(sys.argv[1])


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase, ABC):
    pass


class Database:
    def __init__(self):
        self.db = ReconnectMySQLDatabase(environ[c.ENV_DB_NAME], host=environ[c.ENV_DB_HOST],
                                         port=int(environ[c.ENV_DB_PORT]), user=environ[c.ENV_DB_USER],
                                         password=environ[c.ENV_DB_PASSWORD])

    def get_db(self):
        if self.db.is_connection_usable():
            return self.db

        self.db.connect()
        return self.db

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()
