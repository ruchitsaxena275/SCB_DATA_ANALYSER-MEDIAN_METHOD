import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def fetch_html(login_url, username, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(login_url)
        time.sleep(3)  # wait for page load

        # Enter login credentials
        driver.find_element(By.NAME, "email").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)

        time.sleep(5)  # wait for redirect

        html = driver.page_source
        return html

    except Exception as e:
        print("Login failed:", e)
        return None

    finally:
        driver.quit()
