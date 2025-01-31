import os
from typing import List, Optional
from urllib.parse import quote_plus

import pymongo
import yaml
from klinklang import logger
from pydantic import BaseModel, model_validator

file_dir = os.path.dirname(os.path.abspath(__file__))


class Database(BaseModel):
    database_name: str
    host: str
    password: str
    username: str

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


class Domain(BaseModel):
    domain_name: str


class Proxy(BaseModel):
    proxy: str = None
    rotating: bool = False


class AccountSaveConfig(BaseModel):
    save_to_file: bool = False
    format: str = "{email}, {username}, {password}, {dob}"


class Config(BaseModel):
    database: Database
    domains: List[Domain]
    proxies: Optional[List[Proxy]] = []
    accounts: AccountSaveConfig = AccountSaveConfig()
    proxy_file: str = None
    show_total_accounts: bool = False
    show_chart: bool = True  # New flag to control the domain account chart
    headless: bool = True
    names_generator: bool = False
    account_password: Optional[str] = None
    mail_prefix: Optional[str] = None
    proxy_region: Optional[str] = None
    random_subdomain: bool = False
    subdomain_length: int = 32
    proxy_cooldown: int = 1900
    binary_location: Optional[str] = None
    email_code_waiting_max: int = 180
    additional_sleep_time: int = 0
    webdriver_max_wait: int = 30
    network_blocks: Optional[List[str]] = None
    max_accounts_per_domain: Optional[int] = -1  # Default to -1 for unlimited accounts

    @model_validator(mode="after")
    def load_proxie_file(self):
        proxie_file = self.proxy_file
        proxies: List[Proxy] = self.proxies

        if proxie_file:
            logger.info(f"Loading proxies from {os.path.join(file_dir, proxie_file)}")
            with open(os.path.join(file_dir, proxie_file), "r") as f:
                loaded_proxies = f.readlines()

            for proxy in loaded_proxies:
                proxy = proxy.strip()
                rotating = False
                if proxy.endswith("/rotating"):
                    rotating = True
                    proxy = proxy.replace("/rotating", "")
                if proxy:
                    proxies.append(Proxy(proxy=proxy, rotating=rotating))
        self.proxies = proxies
        if self.max_accounts_per_domain == -1:
            logger.info("No max_accounts_per_domain specified; defaulting to unlimited accounts.")
        else:
            logger.info(f"Max accounts per domain set to {self.max_accounts_per_domain}.")


def load_config():
    logger.info("Loading config...")
    with open(os.path.join(file_dir, "config.yml"), "r") as f:
        config = yaml.safe_load(f)
    logger.info("Loaded config")
    return Config(**config)
