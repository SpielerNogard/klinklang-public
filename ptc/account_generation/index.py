import datetime
import hashlib
import json
import os
import random
import string
import sys
import time
import traceback
from itertools import cycle
from pprint import pprint
from typing import Union, List

import pymongo
import requests
from config import Config, Proxy, load_config
from klinklang import logger
from klinklang.core.db_return import db_return
from klinklang.core.ptc import PossibleMonths
from klinklang.core.ptc.get_country_for_proxy import get_country_for_proxy
from klinklang.core.ptc.get_random_dob import get_random_dob
from klinklang.core.ptc.random_word_gen import RandomWordGen
from klinklang.core.ptc.timeout import timeout
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

# Create Screenshots directory if it does not exist
file_dir = os.path.dirname(os.path.abspath(__file__))
screenshot_dir = os.path.join(file_dir, "screenshots")
if not os.path.exists(screenshot_dir):
    os.mkdir(screenshot_dir)

word_gen = RandomWordGen()
config = load_config()
SLEEPTIME = config.proxy_cooldown
ADDITIONAL_SLEEP = config.additional_sleep_time
WEBDRIVER_MAX_WAIT = config.webdriver_max_wait


def get_proxies(config: Config):
    """
    Get all proxies from the config
    """
    if not config.proxies:
        logger.warning("No proxies found, using your IP")
        return [Proxy()]
    return config.proxies


@timeout(seconds=60 * 5)
def get_code_for_email(
    email: str,
    collection: pymongo.collection.Collection,
    counter: int = 0,
    max_counter: int = 180,
) -> str:
    """
    Search the database for the code for the email

    Parameters
    ----------
    email : str
        The email for which the code should be searched
    collection : pymongo.collection.Collection
        The collection in which the code should be searched
    counter : int, optional
        current counter, used for recursion
    max_counter : int, optional
        maximum number of tries before timeout
    """
    code = db_return(collection.find({"email": email}))
    if not code:
        if counter <= max_counter:
            time.sleep(1)
            return get_code_for_email(
                email, collection, counter=counter + 1, max_counter=max_counter
            )
        logger.error(
            f"Max attempts exceeded for {email}. Aboarding account generation."
        )
        raise TimeoutError(f"Max attempts exceeded for {email}")
    else:
        return code[0]["code"]


def generate_account(
    domain: str,
    password: str = None,
    prefix: str = None,
    proxy: str = None,
    proxy_region: str = None,
    random_subdomain: bool = False,
    subdomain_length: int = 32,
) -> dict:
    """
    Generate credentials for an account

    Parameters
    ----------
    domain : str
        The domain for the account
    password : str, optional
        The password for the account
    prefix : str, optional
        The prefix for the email
    proxy : str, optional
        The proxy for the account
    proxy_region : str, optional
        The region for the proxy
    random_subdomain : bool, optional
        If the subdomain should be random
    subdomain_length : int, optional
        The length of the subdomain
    """
    username = word_gen.generate_username()
    if random_subdomain:
        subdomain = word_gen.generate_username().replace("_", "")
        while len(subdomain) < subdomain_length:
            subdomain = subdomain + word_gen.generate_username().replace("_", "")
        subdomain = subdomain[:subdomain_length]
        subdomain = subdomain.lower()
        domain = ".".join([subdomain, domain])
        logger.info(f"Random subdomain: {domain}")

    region = get_country_for_proxy(proxy=proxy, region=proxy_region)
    year_, month_, day_ = get_random_dob()

    day_of_birth = f"{year_}-{PossibleMonths.index(month_)+1}-{day_}"
    mail = "@".join([username, domain])
    if prefix:
        mail = "@".join(["+".join([prefix, username]), domain])

    account = {
        "email": mail,
        "username": username,
        "screenname": f"{username}"[:15],
        "password": password or word_gen.generate_password(),
        "dob": day_of_birth,
        "dob_year": year_,
        "dob_month": month_,
        "dob_day": day_,
        "region": region,
    }
    return account


def get_own_ip():
    """
    Get the own IP address
    """
    return requests.get("https://checkip.amazonaws.com").text.strip()


def insert_usage(proxy: str = None, rotating: bool = False):
    if not proxy:
        proxy = get_own_ip()
    if rotating is True:
        return

    db = config.database.client()["ips"]
    db.delete_many({"ip": proxy})
    db.insert_one(
        {"ip": proxy, "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    )


def generate_secret():
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=30))
    hash_object = hashlib.md5(random_string.encode())
    random_hash = hash_object.hexdigest()
    return random_hash


def get_total_number_of_accounts() -> int:
    database_client = config.database.client()
    accounts = db_return(database_client["accounts"].find())
    return len(accounts)


def save_account(account: dict):
    database_client = config.database.client()
    database_client["accounts"].insert_one(account)
    logger.info("Account saved")


def create_driver(config: Config, proxy: str = None, counter: int = 0):
    try:
        kwargs = {}
        if proxy:
            kwargs["proxy"] = proxy

        if config.binary_location:
            kwargs["binary_location"] = config.binary_location
        # kwargs['binary_location'] = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        browser_name = "chrome"
        logger.info(f"Starting {browser_name} Driver...")
        chromium_args = "--lang=en-us, --disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints"
        kwargs["chromium_arg"] = chromium_args
        driver = Driver(uc=True, headless2=config.headless, **kwargs)

        # stealth(driver, languages=["en-US", "en"], vendor="Google Inc.",
        #      webgl_vendor="Intel Inc.",
        #     renderer="Intel Iris OpenGL Engine", fix_hairline=True, )
        # driver.maximize_window()
        driver.delete_all_cookies()

        if config.network_blocks:
            logger.info(f"Enabling network blocks: {config.network_blocks}")
            driver.execute_cdp_cmd(
                "Network.setBlockedURLs",
                {
                    "urls": config.network_blocks,
                },
            )
            driver.execute_cdp_cmd("Network.enable", {})
            driver.refresh()

        logger.info("Refreshing cookies")
        return driver
    except:
        logger.error("Failed to start driver ... Trying again.")
        if counter <= 10:
            return create_driver(proxy=proxy, counter=counter + 1, config=config)
        raise


def access_ptc_site(driver):
    logger.info("Starting Access PTC site...")
    # driver.uc_open_with_disconnect("https://join.pokemon.com/", 2.2)
    # time.sleep(200)
    driver.get("https://join.pokemon.com/")
    WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
    driver.save_screenshot(os.path.join(screenshot_dir, "access-ptc.png"))

    # driver.add_cookie(
    #     {"name": "dob", "value": "183855600000", "domain": "join.pokemon.com",
    #      "path": "/"})
    # driver.add_cookie(
    #     {"name": "country", "value": "AU", "domain": "join.pokemon.com", "path": "/"})
    # driver.refresh()
    # time.sleep(1200000)


def submit_account_details(driver: Driver, account: dict):
    logger.info("Submitting details about my person, yes i am indeed a person")
    try:
        submit_button = WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            EC.presence_of_element_located((By.ID, "ageGateSubmit"))
        )
        logger.info("Found submit button.")
        driver.save_screenshot(os.path.join(screenshot_dir, "submit_button.png"))
    except:
        logger.info("Not Found submit button.")
        driver.save_screenshot(os.path.join(screenshot_dir, "submit_button.png"))
        return False

    try:
        driver.find_element(
            "xpath",
            "//h1[contains(text(), 'Enter your country or region and your birthdate')]",
        )
    except:
        logger.error("Failed to find header")
        driver.save_screenshot(os.path.join(screenshot_dir, "header.png"))
        return False

    country = driver.find_element(by=By.ID, value="country-select")
    year = driver.find_element(by=By.ID, value="year-select")
    month = driver.find_element(by=By.ID, value="month-select")
    day = driver.find_element(by=By.ID, value="day-select")

    country.send_keys(account["region"])
    year.send_keys(f"{account['dob_year']}")
    month.send_keys(f"{account['dob_month']}")
    day.send_keys(f"{account['dob_day']}")

    submit_button.click()
    driver.save_screenshot(os.path.join(screenshot_dir, "account_details.png"))
    return True


def bypass_imperva(driver: Driver, account: dict):
    logger.info("Hello imperva, lets fight")
    driver.save_screenshot(os.path.join(screenshot_dir, "imperva.png"))
    try:
        WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            lambda driver: driver.find_element(
                "xpath", "//button[contains(text(), 'I Am Sure')]"
            )
        )
        driver.find_element("xpath", "//button[contains(text(), 'I Am Sure')]").click()
    except:
        WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            lambda driver: driver.find_element(
                "xpath", "//button[contains(text(), 'Yes, it is')]"
            )
        )
        driver.find_element("xpath", "//button[contains(text(), 'Yes, it is')]").click()

    email = driver.find_element(by=By.ID, value="email-text-input")
    confirm_email = driver.find_element(by=By.ID, value="confirm-text-input")

    email.send_keys(account["email"])
    confirm_email.send_keys(account["email"])

    driver.find_element("xpath", "//button[contains(text(), 'Continue')]").click()
    try:
        WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            lambda driver: driver.find_element(
                "xpath",
                "//div[contains(text(), 'Please review and accept the Terms of Use')]",
            )
        )
    except:
        logger.info("Failed to bypass Imperva Bot Detection. Aborting and retrying...")
        return False
    logger.info("Bypassed!")
    return True


def enter_username_and_password(driver: Driver, account: dict):
    logger.info("Entering username and password.")
    driver.find_element("xpath", "//button[contains(text(), 'Accept')]").click()
    time.sleep(1)
    driver.find_element("xpath", "//button[contains(text(), 'Accept')]").click()
    logger.info("Accepted data protection")

    driver.find_element("xpath", "//button[contains(text(), 'Skip')]").click()
    WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
        lambda driver: driver.find_element(
            "xpath", "//h1[contains(text(), 'Enter the username and password')]"
        )
    )
    username_input = driver.find_element(by=By.ID, value="Username-text-input")
    # username_input.click()
    # driver.uc_gui_press_keys(list(account["username"]))
    try:
        password_input = driver.find_element(by=By.ID, value="password-text-input")
    except:
        password_input = driver.find_element(by=By.ID, value="password-text-input-test")

    username_input.send_keys(account["username"])
    password_input.send_keys(account["password"])

    driver.find_element("xpath", "//button[contains(text(), 'Create Account')]").click()
    logger.info("Inserted account data")

    WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
        lambda driver: driver.find_element(
            "xpath", "//button[contains(text(), 'I Am Sure')]"
        )
    )

    driver.find_element("xpath", "//button[contains(text(), 'I Am Sure')]").click()
    return True


def send_code(driver, account: dict):
    try:
        WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            lambda driver: driver.find_element(by=By.ID, value="code-text-input")
        )
        logger.info("Code input field is existing")
        driver.save_screenshot(os.path.join(screenshot_dir, "code_input.png"))
    except:
        logger.info(
            "No Code input field found. Stop your fuckery imperva. Accept the loose"
        )
        driver.save_screenshot(os.path.join(screenshot_dir, "code_input.png"))
        return False

    logger.info("Waiting for code from email")
    code = get_code_for_email(
        email=account["email"],
        collection=config.database.client()["codes"],
        max_counter=config.email_code_waiting_max,
    )
    codeinput = driver.find_element(by=By.ID, value="code-text-input")
    logger.info(f"Inserting {code=} for {account['email']}")
    codeinput.send_keys(code)
    driver.find_element("xpath", "//button[contains(text(), 'Continue')]").click()
    logger.info("Waiting for verification from server...")
    try:
        WebDriverWait(driver, WEBDRIVER_MAX_WAIT).until(
            lambda driver: driver.find_element(
                "xpath", "//h1[contains(text(), 'Success')]"
            )
        )
        driver.save_screenshot(os.path.join(screenshot_dir, "verify.png"))
        return True
    except:
        logger.info("Failed to verify account. Aborting and retrying...")
        driver.save_screenshot(os.path.join(screenshot_dir, "verify.png"))
        return False


def save_account_to_file(account: dict, format: str):
    file_name = f"{datetime.datetime.now(datetime.timezone.utc).date().isoformat()}.txt"
    format = (
        format.replace("{email}", f'{account["email"]}')
        .replace("{username}", f'{account["username"]}')
        .replace("{password}", f"{account['password']}")
        .replace("{dob}", f'{account["dob"]}')
        .replace("{region}", f'{account["region"]}')
    )
    if not os.path.exists(os.path.join(file_dir, "accounts")):
        os.mkdir(os.path.join(file_dir, "accounts"))
    with open(os.path.join(file_dir, "accounts", file_name), "a") as f:
        f.write(f"{format}\n")


def generate(
    domain: str,
    config: Config,
    proxy: str = None,
    save_to_file: bool = False,
    format: str = "{email}, {username}, {password}, {dob}",
):
    generated = False
    start = time.time()
    account = generate_account(
        domain=domain,
        password=config.account_password,
        prefix=config.mail_prefix,
        proxy=proxy or get_own_ip(),
        proxy_region=config.proxy_region,
        random_subdomain=config.random_subdomain,
        subdomain_length=config.subdomain_length,
    )
    logger.info(f"Starting account creation: {account=}")
    logger.info(f'{"*" * 10} {proxy or get_own_ip()} {"*" * 10}')
    driver = create_driver(proxy=proxy, config=config)
    time.sleep(ADDITIONAL_SLEEP)
    try:
        access_ptc_site(driver)
        time.sleep(ADDITIONAL_SLEEP)
        if submit_account_details(driver, account=account):
            time.sleep(ADDITIONAL_SLEEP)
            if bypass_imperva(driver, account):
                time.sleep(ADDITIONAL_SLEEP)
                enter_username_and_password(driver, account)
                time.sleep(ADDITIONAL_SLEEP)
                if send_code(driver, account):
                    logger.info("Account was successfully activated. Saving to DB")
                    save_account(account)
                    time_needed = time.time() - start
                    logger.info(f"Account generated in {time_needed} seconds")
                    if save_to_file is True:
                        save_account_to_file(account=account, format=format)

                    generated = True
            else:
                logger.error("Blocked by imperva")
        else:
            logger.error("Blocked by website")
    except Exception as e:
        logger.error("Account generation failed.")
        logger.error(f"{traceback.format_exc()}")
        driver.save_screenshot(os.path.join(screenshot_dir, "error.png"))
    driver.save_screenshot(os.path.join(screenshot_dir, "success.png"))
    driver.quit()
    return generated


def get_success_full_proxies(proxy_stats: dict, number: int = 10, success: bool = True):
    stats = []
    for proxy, used in proxy_stats.items():
        success_ = used.count(True)
        failed = used.count(False)
        stats.append(
            {"name": proxy, "success": success_, "failed": failed, "total": len(used)}
        )
    key = "failed"
    if success:
        key = "success"
    sorted_stats = sorted(stats, key=lambda x: x[key], reverse=True)
    for stat in sorted_stats[:number]:
        logger.info_cyan(stat)


def find_last_used_for_proxy(
    proxy: str, config: Config, usage_data: List[dict]
) -> datetime.datetime:
    used = [datapoint for datapoint in usage_data if datapoint["ip"] == proxy]

    last_used = datetime.datetime.fromtimestamp(1, tz=datetime.timezone.utc)
    for item in used:
        found_time = datetime.datetime.fromisoformat(item["ts"])
        if found_time > last_used:
            last_used = found_time

    return last_used


def find_oldest_proxy(
    config: Config, proxies: List[Proxy]
) -> Union[Proxy, datetime.datetime]:
    rotating_proxies = [proxy for proxy in proxies if proxy.rotating]
    if rotating_proxies:
        return random.choice(rotating_proxies)

    db = config.database.client()["ips"]
    used = db_return(db.find())

    used_for_proxies = []
    for proxy in proxies:
        last_used = find_last_used_for_proxy(
            proxy.proxy or get_own_ip(), config=config, usage_data=used
        )
        used_for_proxies.append({"proxy": proxy.proxy, "last_used": last_used})

    sorted_used = sorted(used_for_proxies, key=lambda x: x["last_used"])
    for proxy in sorted_used:
        last_used = proxy["last_used"]
        if last_used + datetime.timedelta(seconds=SLEEPTIME) < datetime.datetime.now(
            datetime.timezone.utc
        ):
            logger.info(f'{proxy["proxy"]} is the oldest proxy. {last_used=}')
            if proxy["proxy"] is None:
                return Proxy()
            return Proxy(proxy=proxy["proxy"])
    logger.warning("No proxy is usable")
    logger.info(f"Oldest proxy is {sorted_used[0]}")
    return sorted_used[0]["last_used"]


def _add_to_proxy_stats(proxy: str, success: bool = True):
    try:
        if not os.path.exists(os.path.join(file_dir, "stats")):
            os.mkdir(os.path.join(file_dir, "stats"))

        if os.path.exists(os.path.join(file_dir, "stats", "proxies.json")):
            with open(os.path.join(file_dir, "stats", "proxies.json"), "r") as in_file:
                proxy_stats = json.load(in_file)
        else:
            proxy_stats = []

    except:
        proxy_stats = []

    proxy_stats.append(
        {
            "proxy": proxy,
            "success": success,
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )

    with open(os.path.join(file_dir, "stats", "proxies.json"), "w") as f:
        json.dump(proxy_stats, f)


def _add_to_domain_stats(domain: str, success: bool = True):
    try:
        if not os.path.exists(os.path.join(file_dir, "stats")):
            os.mkdir(os.path.join(file_dir, "stats"))

        if os.path.exists(os.path.join(file_dir, "stats", "domains.json")):
            with open(os.path.join(file_dir, "stats", "domains.json"), "r") as in_file:
                domain_stats = json.load(in_file)
        else:
            domain_stats = []
    except:
        domain_stats = []

    domain_stats.append(
        {
            "domain": domain,
            "success": success,
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )

    with open(os.path.join(file_dir, "stats", "domains.json"), "w") as f:
        json.dump(domain_stats, f)


if __name__ == "__main__":
    config = load_config()
    pprint(config.dict())

    proxy_stats = {}
    domain_stats = {}

    usable_proxies = get_proxies(config)
    domains = cycle(config.domains)
    account_save_config = config.accounts

    counter = 0
    send = False
    while True:
        try:
            domain = next(domains)
            # proxy = next(proxies)
            proxy = find_oldest_proxy(config, usable_proxies)
            if isinstance(proxy, Proxy):
                # if proxy_usable(config, proxy.proxy, rotating=proxy.rotating):
                insert_usage(proxy.proxy, proxy.rotating)

                generated = generate(
                    domain=domain.domain_name,
                    proxy=proxy.proxy,
                    save_to_file=account_save_config.save_to_file,
                    format=account_save_config.format,
                    config=config,
                )
                if generated is True:
                    counter += 1

                    # insert proxy stats
                    _add_to_proxy_stats(proxy.proxy or get_own_ip(), success=True)
                    # insert domain stats
                    _add_to_domain_stats(domain.domain_name, success=True)
                else:
                    # insert proxy stats
                    _add_to_proxy_stats(proxy.proxy or get_own_ip(), success=False)

                    # insert domain stats
                    _add_to_domain_stats(domain.domain_name, success=False)
            else:
                time_to_sleep = (
                    (proxy + datetime.timedelta(seconds=SLEEPTIME))
                    - datetime.datetime.now(datetime.timezone.utc)
                ).total_seconds()
                if time_to_sleep > 0:
                    logger.info(
                        f"You will hear me in {datetime.timedelta(seconds=time_to_sleep)}. Please dont forget me until then 😢."
                    )
                    time.sleep(time_to_sleep)
        except Exception as e:
            logger.error(f"OOPS something went wrong")
            logger.error(f"{traceback.format_exc()}")
            sys.exit()

        if counter % 10 == 0 and counter != 0 and send is False:
            send = True
        else:
            logger.info_cyan(f"Generated accounts in this session: {counter}")
            if config.show_total_accounts:
                logger.info_cyan(
                    f"Total generated accounts with klinklang: {get_total_number_of_accounts()}"
                )
            send = False
