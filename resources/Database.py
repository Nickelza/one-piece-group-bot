import sys
from abc import ABC

from dotenv import load_dotenv
from peewee import *
from playhouse.shortcuts import ReconnectMixin

import resources.Environment as Env

load_dotenv(sys.argv[1])


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase, ABC):
    pass


class Database:
    def __init__(self):
        self.db = ReconnectMySQLDatabase(Env.DB_NAME.get(), host=Env.DB_HOST.get(), port=int(Env.DB_PORT.get()),
                                         user=Env.DB_USER.get(), password=Env.DB_PASSWORD.get(),
                                         charset='utf8mb4')

    def get_db(self):
        if self.db.is_connection_usable():
            return self.db

        self.db.connect()
        return self.db

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()
