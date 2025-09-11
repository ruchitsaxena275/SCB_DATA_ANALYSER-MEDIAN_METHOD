from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setup headless Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")  # Comment out this line to see the browser
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)

def login(driver, login_url, username, password):
    driver.get(login_url)
    time.sleep(2)  # Let page load

    # Enter username and password using provided 'name' attributes
    driver.find_element(By.NAME, "email").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Click SIGN IN button using XPath to match button text
    driver.find_element(By.XPATH, "//button[text()='SIGN IN']").click()
    time.sleep(5)  # Wait for login to complete

def check_for_update(driver, target_url, last_content):
    driver.get(target_url)
    time.sleep(5)  # Wait page fully loads

    # Replace 'target_element_id' with actual element ID or XPath for the monitored content on POSOCO portal.
    # For example purposes, let's assume an element with id 'updateContent'
    try:
        element = driver.find_element(By.ID, "updateContent")
        current_content = element.text
    except:
        current_content = ""

    # Check for content change
    if current_content != last_content:
        return current_content, True
    return last_content, False

if __name__ == "__main__":
    login_url = "https://oms.nrldc.in/posoco/home?_logout=true&status=false"      # Replace with actual login URL
    data_url = "https://oms.nrldc.in/posoco/shutdown?action=otherlist&list=true" # Replace with actual page URL to monitor
    username = "Junaoutage"                         # Replace with actual username
    password = "junaoutage123"                      # Replace with actual password
    last_content = ""

    login(driver, login_url, username, password)

    while True:
        last_content, updated = check_for_update(driver, data_url, last_content)
        if updated:
            print("New update detected!")
            # Trigger your desktop notification here
        else:
            print("No change detected.")
        time.sleep(300)  # Check every 5 minutes
