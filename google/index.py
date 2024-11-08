import datetime
import os
import random
import time
from itertools import cycle
from pprint import pprint


from smspool import SMSPool

from config import Config, load_config
from klinklang import logger
from klinklang.core.ptc.random_word_gen import RandomWordGen
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from seleniumbase import Driver

word_gen = RandomWordGen()
gen_config = load_config()


class GoogleAccountGenerator:
    def __init__(self):
        self.ignore_countries = []


obj = GoogleAccountGenerator()
sms_pool = SMSPool(api_key=gen_config.sms_pool_api_key, service_name="Google/Gmail")


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


def check_correct_page(
    driver, page_text: str, counter: int = 0, allow_skip: bool = False
):
    try:
        driver.find_element("xpath", f"//span[text()='{page_text}']")
        print(f"Entered correct page: {page_text}")
        time.sleep(1)
        return True
    except:
        if counter <= 10:
            time.sleep(1)
            return check_correct_page(
                driver=driver,
                page_text=page_text,
                counter=counter + 1,
                allow_skip=allow_skip,
            )
        else:
            if allow_skip:
                print(f"skipped page: {page_text}")
                time.sleep(1)
                return False
    raise Exception(f"Could not find correct page {page_text=}")


def next_page(driver):
    next_button = driver.find_element("xpath", "//span[text()='Next']")
    next_button.click()


def page_one(driver):
    check_correct_page(driver, "Create a Google Account")
    first_name = driver.find_element("xpath", "//input[@name='firstName']")
    last_name = driver.find_element("xpath", "//input[@name='lastName']")

    first_name.send_keys(word_gen.generate_username(upper_limit=10, only_chars=True))
    last_name.send_keys(word_gen.generate_username(upper_limit=10, only_chars=True))

    next_page(driver)


def page_two(driver):
    check_correct_page(driver, "Basic information")

    day = driver.find_element("xpath", "//input[@id='day']")
    month_element = driver.find_element("xpath", "//select[@id='month']")
    month = Select(month_element)
    year = driver.find_element("xpath", "//input[@id='year']")

    day.send_keys(random.randint(1, 28))
    month.select_by_index(random.randint(1, 12))
    current_year = datetime.datetime.now().year
    year.send_keys(random.randint(current_year - 30, current_year - 19))
    time.sleep(2)

    gender_element = driver.find_element("xpath", "//select[@id='gender']")
    gender = Select(gender_element)
    gender.select_by_index(random.randint(1, 3))

    next_page(driver)


def page_three(driver):
    check_correct_page(driver, "Choose how you’ll sign in", allow_skip=True)
    try:
        gmail_adress = driver.find_element(
            "xpath", "//div[@data-value='1' and @role='radio']"
        )
        gmail_adress.click()
        time.sleep(1)

        next_page(driver)
    except:
        print("Google has skipped third page")


def page_four(driver):
    check_correct_page(driver, "Choose your Gmail address", allow_skip=True)
    time.sleep(3)

    def find_and_add_username():
        username = driver.find_element("xpath", "//input[@name='Username']")
        random_username = word_gen.generate_username(upper_limit=30)
        username.send_keys(random_username)
        print(f"inserted username: {random_username}")
        return random_username

    try:
        selector = driver.find_element(
            "xpath", "//div[@aria-posinset='3' and @role='radio']"
        )
        selector.click()
        print("Gmail is giving me mail adresses")
        username = find_and_add_username()
    except:
        username = find_and_add_username()

    next_page(driver)
    return username


def page_five(driver):
    check_correct_page(driver, "Create a strong password")
    generated_password = word_gen.generate_password()
    password = driver.find_element("xpath", "//input[@name='Passwd']")
    password_again = driver.find_element("xpath", "//input[@name='PasswdAgain']")
    password.send_keys(generated_password)
    password_again.send_keys(generated_password)
    print(f"Inserted password: {generated_password}")

    next_page(driver)
    return generated_password


def page_six(driver, ignore_countries: list = None, counter: int = 0):
    time.sleep(4)
    phone_number = driver.find_element("xpath", "//input[@id='phoneNumberId']")
    print("Entered correct page: Confirm you're not a robot")
    # check_correct_page("Confirm you're not a robot", allow_skip=True)
    ignore_countries = obj.ignore_countries

    def check_for_errors():
        ERRORS = [
            "This phone number cannot be used for verification.",
            "This phone number format is not recognized. Please check the country and number.",
            "This phone number has been used too many times",
            "There was a problem verifying your phone number",
        ]
        for error in ERRORS:
            try:
                driver.find_element("xpath", f"//div[text()='{error}']")
                print(f"Error found: {error}")
                return error
            except:
                pass
        print("No Error found")
        return None

    found = check_correct_page(driver, "Error", allow_skip=True)
    if found:
        print("Rate limit reached")
        driver.quit()
        raise Exception("Rate limit reached")

    order = sms_pool.order_sms(
        service=sms_pool._service, ignore_countries=ignore_countries
    )
    for a in range(50):
        phone_number.send_keys(Keys.BACK_SPACE)
    phone_number.send_keys(f"+{order.cc} {order.phonenumber}")
    # for a in range(len(str(order.number)) + 2):
    #     phone_number.send_keys(Keys.BACK_SPACE)
    # phone_number.send_keys(f"{order.phonenumber}")
    time.sleep(10)
    next_button = driver.find_element("xpath", "//span[text()='Next']")
    next_button.click()
    time.sleep(4)
    error = check_for_errors()
    if error:
        # print('Refunding SMS')
        # sms_pool.refund(order_id=order.order_id)
        if error != "This phone number has been used too many times":
            obj.ignore_countries.append(order.country)
        print(f"Error found: {error}")
        if counter <= 1000:
            return page_six(
                driver=driver, ignore_countries=ignore_countries, counter=counter + 1
            )

        print("Error found")
        driver.quit()
        raise Exception("Error found")
    return f"{order.number}"


def page_seven(driver, phone_number: str):
    def get_code(phone_number):
        resp = sms_pool.order_history(phone_number=phone_number)
        for item in resp:
            status = item["status"]

            if status == "pending":
                time_left = item["time_left"]
                order_id = item["order_code"]

                time.sleep(2)
                print(item)
                return get_code(phone_number=phone_number)
                # resend code
                # resend_button = driver.find_element("xpath", "//span[text()='Get new code']")
                # resend_button.click()
                # time.sleep(1)
                # phone_number = page_six(driver=driver)
                # return page_seven(driver=driver, phone_number=phone_number)
            elif status == "completed":
                print(item)
                return item["code"]
            else:
                print(item)

    check_correct_page(driver, "Enter the code")
    code_input = driver.find_element("xpath", "//input[@name='code']")
    sms_code = get_code(phone_number)

    code_input.send_keys(sms_code)

    next_page(driver)


def page_eight(driver):
    check_correct_page(driver, "Add recovery email", allow_skip=True)
    next_button = driver.find_element("xpath", "//span[text()='Skip']")
    next_button.click()
    time.sleep(4)


def page_nine(driver):
    found = check_correct_page(driver, "Add phone number", allow_skip=True)
    if found:
        next_button = driver.find_element("xpath", "//span[text()='Skip']")
        next_button.click()
    time.sleep(4)


def page_ten(driver):
    found = check_correct_page(driver, "Review your account info", allow_skip=True)
    if found:
        next_button = driver.find_element("xpath", "//span[text()='Next']")
        next_button.click()
    time.sleep(4)


def page_eleven(driver):
    found = check_correct_page(driver, "Choose your settings", allow_skip=True)
    if found:
        selector = driver.find_element(
            "xpath", "//div[@aria-posinset='1' and @role='radio']"
        )
        selector.click()
        print("Gmail is giving me mail adresses")

        next_button = driver.find_element("xpath", "//span[text()='Next']")
        next_button.click()
    time.sleep(4)


def page_eleven2(driver):
    found = check_correct_page(driver, "Choose your settings", allow_skip=True)
    if found:
        next_button = driver.find_element("xpath", "//span[text()='Accept all']")
        next_button.click()
        time.sleep(4)


def page_twelve(driver):
    found = check_correct_page(driver, "Confirm your settings", allow_skip=True)
    if found:
        next_button = driver.find_element("xpath", "//span[text()='Confirm']")
        next_button.click()
        time.sleep(4)


def page_thirteen(driver):
    check_correct_page(driver, "Privacy and Terms", allow_skip=True)
    next_button = driver.find_element("xpath", "//span[text()='I agree']")
    next_button.click()
    time.sleep(4)

    try:
        driver.find_element("xpath", "//span[text()='Confirm']").click()
        time.sleep(4)
    except:
        pass


def page_fourteen(driver, username: str, password: str):
    # check_correct_page("Privacy and Terms", allow_skip=True)
    time.sleep(10)
    try:
        driver.find_element("xpath", "//div[text()='Home']")
        print("Account created successfully")
        driver.quit()
    except:
        print("Could not find home page")
        time.sleep(200)
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "gmail_accounts.txt"), "a") as file:
        file.write(f"{username}, {password}\n")
    print("Account saved")


def generate_google_account(config: Config, proxy: str = None):
    driver = create_driver(config, proxy=proxy)
    url = "https://accounts.google.com/signup"
    driver.get(url)
    print("Opened google signup page")

    page_one(driver)
    page_two(driver)
    page_three(driver)
    username = page_four(driver)
    password = page_five(driver)
    phone_number = page_six(driver)
    page_seven(driver=driver, phone_number=phone_number)
    page_eight(driver)
    page_nine(driver)
    page_ten(driver)
    page_eleven(driver)
    page_eleven2(driver)
    page_twelve(driver)
    page_thirteen(driver)
    page_fourteen(driver=driver, username=username, password=password)


if __name__ == "__main__":
    pprint(gen_config.dict())
    proxies = cycle(gen_config.proxies)
    while True:
        proxy=None
        if gen_config.proxies:
            proxy = next(proxies).proxy
            print(f"Using proxy: {proxy=}")


        try:
            print(f"{obj.ignore_countries=}")
            generate_google_account(config=gen_config, proxy=proxy)
        except Exception as exc:
            print(exc)
