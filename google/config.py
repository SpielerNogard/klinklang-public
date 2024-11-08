import os
from typing import List, Optional

import yaml
from klinklang import logger
from pydantic import BaseModel, model_validator
file_dir = os.path.dirname(os.path.abspath(__file__))


class Proxy(BaseModel):
    proxy: str = None
    rotating: bool = False


class Config(BaseModel):
    proxies: Optional[List[Proxy]] = []
    proxy_file: str = None
    sms_pool_api_key: str
    binary_location: Optional[str] = None
    headless: bool = True
    network_blocks: Optional[List[str]] = None

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
        # return values


def load_config():
    logger.info("Loading config...")
    with open(os.path.join(file_dir, "config.yml"), "r") as f:
        config = yaml.safe_load(f)
    logger.info("Loaded config")
    return Config(**config)
