import os
import random

import requests
from klinklang import logger
from klinklang.core.ptc import POSSIBLE_REGIONS


def get_country_for_proxy(proxy: str, region: str = None):
    if region and region in POSSIBLE_REGIONS:
        logger.info(f"{region=} was given through config file. Continuing.")
        return region
    if region and region not in POSSIBLE_REGIONS:
        logger.error(f"{region=} was given through config file but is invalid.")
        logger.info(f"{POSSIBLE_REGIONS=}")

    proxies = {
        "http": proxy,
        "https": proxy,
    }

    try:
        resp = requests.get(f"https://api.country.is", proxies=proxies)
        country_code = resp.json()["country"]
        found_countries = [
            country
            for country in POSSIBLE_REGIONS.keys()
            if POSSIBLE_REGIONS[country] == country_code
        ]
        if found_countries:
            country = found_countries[0]
            logger.info(f"Found {country=} for proxy {proxy}")
            return country

        logger.warning(
            f"Found {country_code=} for proxy {proxy}. This is not allowed. Choosing random region"
        )
        return random.choice(list(POSSIBLE_REGIONS.keys()))
    except:
        logger.warning(
            "Error occured while checking proxy region. Continuing with random region"
        )
        return random.choice(list(POSSIBLE_REGIONS.keys()))
