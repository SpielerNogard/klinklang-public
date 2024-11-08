from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver
import time

# 2captcha API key
API_KEY = "cbad27ee8123a388a"


def create_driver(counter: int = 0):
    try:
        kwargs = {}
        browser_name = "chrome"
        print(f"Starting {browser_name} Driver...")
        chromium_args = "--lang=en-us, --disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints"
        kwargs["chromium_arg"] = chromium_args
        driver = Driver(uc=True, headless2=False, **kwargs)
        driver.delete_all_cookies()

        print("Refreshing cookies")

        # driver.get("https://www.google.com/recaptcha")
        # cookie = {
        #     "name": "_GRECAPTCHA",
        #     "value": "09AGteOyrvsastbYNXyN7iBK8ouEooHbQJ9mv92BXxuenaNGZgM_4ElN3az9FXYUiIEOSNPd5aUX98wu65zOsEeUU",
        #     "domain": "www.google.com",
        #     "path": "/recaptcha",
        #     "expiry": int(time.time()) + 31536000,  # 1 year from now,
        # }
        #
        # driver.add_cookie(cookie)

        return driver
    except Exception as exc:
        print(f"Failed to start driver ... Trying again. {exc}")
        if counter <= 10:
            return create_driver(counter=counter + 1)
        raise


def input_email(driver, username):
    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    driver.execute_script(f"arguments[0].value = '{username}';", email_input)
    # email_input.uc_click()
    # driver.uc_gui_press_keys(username)
    time.sleep(5)
    next_button = driver.find_element(By.XPATH, "//button[contains(., 'Next')]")
    next_button.uc_click()
    time.sleep(5)


def check_for_captcha(driver, counter: int = 0):
    # time.sleep(5)
    try:
        iframe = driver.find_element(
            By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']"
        )
        print("Captcha found")
    except Exception as e:
        print(e)
        print("No Captcha found")
        return

    # # handle captcha
    time.sleep(2)
    if counter == 0:
        driver.uc_gui_click_rc()
        #span_element = driver.find_element(By.XPATH, "//div[contains(@class, 'rc-anchor-center-item')]")
        #span_element.click()
    #time.sleep(5)
    driver.switch_to.frame(iframe)
    print("sending to 2captcha")
    # iframe = driver.find_element(By.XPATH,
    #                             "//iframe[@title='recaptcha challenge expires in two minutes']")

    # Get the name of the iframe
    # iframe_name = iframe.get_attribute("name")
    # iframe_src = iframe.get_attribute("src")
    token_input = driver.find_element(By.XPATH, "//input[@id='recaptcha-token']")
    # Use JavaScript to make the element visible
    #driver.execute_script("arguments[0].style.display = 'block';", token_input)

    verify_button = driver.find_element(By.ID, "recaptcha-verify-button")
    errors = [
        driver.find_element(
            By.XPATH, "//div[@class='rc-imageselect-incorrect-response']"
        ),
        driver.find_element(
            By.XPATH, "//div[@class='rc-imageselect-error-select-more']"
        ),
        driver.find_element(
            By.XPATH, "//div[@class='rc-imageselect-error-dynamic-more']"
        ),
        driver.find_element(
            By.XPATH, "//div[@class='rc-imageselect-error-select-something']"
        ),  # driver.find_element(By.XPATH, "//div[@class='rc-anchor-error-msg-container']")
    ]
    print(driver.current_url)
    print("Found token input")
    from twocaptcha import TwoCaptcha

    solver = TwoCaptcha(API_KEY)
    result = solver.recaptcha(
        sitekey="6LdD2OMZAAAAAAv2xVpeCk8yMtBtY3EhDWldrBbh",  # sitekey
        url=driver.current_url,
    )
    print(result)
    result_code = result["code"]
    print(result_code)
    time.sleep(100)
    driver.execute_script(f"arguments[0].value = '{result_code}';", token_input)
    try:
        verify_button.click()
    except:
        print("Failed to click verify button")
        driver.switch_to.default_content()
        check_for_captcha(driver, 0)

    for error in errors:
        print(error.get_attribute("style"))
        if error.get_attribute("style") != "display: none;":
            print(f"Captcha error: {error.text}")
            solver.report(result["captchaId"], False)

            # button = driver.find_element(By.XPATH, "//button[@id='recaptcha-reload-button']")
            # button.click()
            # print('reloaded captcha')
            driver.switch_to.default_content()
            return check_for_captcha(driver, counter + 1)
    driver.switch_to.default_content()
    print("Captcha handled")
    check_for_captcha(driver, counter + 1)


def handle_login(login_url, username, password):
    driver = create_driver()
    driver.uc_open_with_reconnect(login_url, 4)
    print(driver.current_url)
    input_email(driver, username)
    check_for_captcha(driver)
    time.sleep(30)
