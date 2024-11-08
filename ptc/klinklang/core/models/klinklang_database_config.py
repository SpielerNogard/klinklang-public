from urllib.parse import quote_plus

import pymongo
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    """
    Configuration for the database klinklang is using.

    Parameters
    ----------
    host : str
        The IP of the database.
    username : str
        The username of the database.
    password : str
        The password of the database.
    database_name : str
        The name of the database.
        default: "klinklang"
    """

    host: str
    username: str
    password: str
    database_name: str = "klinklang"

    @property
    def url(self):
        return "mongodb://%s:%s@%s" % (
            quote_plus(self.username),
            quote_plus(self.password),
            f"{self.host}/",
        )

    @property
    def database(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(self.url)

    def client(self):
        return self.database[self.database_name]
