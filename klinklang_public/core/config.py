import time
from typing import List
from typing import Literal
from typing import Optional
from urllib.parse import quote_plus

import pika
import pymongo
import yaml
from pydantic import BaseModel

from klinklang_public import logger


class ExportConfig(BaseModel):
    rate :int = 3600
    destination : Literal['DRAGONITE', 'RDM']
    discord : Optional[str] = None

class DatabaseConfig(BaseModel):
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


class MailServerConfig(BaseModel):
    port: int = 25
    host: str = "0.0.0.0"


class MailBox(BaseModel):
    username: str
    password: str
    imap_server: str
    delete_after_read: bool = True


class MailReaderConfig(BaseModel):
    mailbox: List[MailBox]


class QueueConfig(BaseModel):
    host: str
    username: str
    password: str

    @property
    def url(self):
        url = f"amqp://{self.username}:{self.password}@{self.host}/"
        if self.host in ["localhost", "host.docker.internal", "127.0.0.1"]:
            url = f"{url}%2f"
        return url

    def connect(self) -> pika.adapters.blocking_connection.BlockingChannel:
        try:
            params = pika.URLParameters(self.url)
            params.socket_timeout = 5

            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            return channel
        except Exception as e:
            logger.error(f'Queue connection failed: {e=}')
            time.sleep(10)
            logger.info('Trying again ...')
            return self.connect()


class ProxyConfig(BaseModel):
    use_free: bool = False
    check_before_usage: bool = True

class Domain(BaseModel):
    domain_name: str

class DomainConfig(BaseModel):
    domains:List[Domain]

class Config(BaseModel):
    database: DatabaseConfig
    queue: QueueConfig
    mailserver: Optional[MailServerConfig]
    mailreader: Optional[MailReaderConfig]
    proxies: ProxyConfig
    domains: DomainConfig
    export : Optional[ExportConfig]

def read_config(filename: str = "config.yml") -> Config:
    with open(filename, "r") as config_file:
        config = yaml.safe_load(config_file)
    return Config(**config)
