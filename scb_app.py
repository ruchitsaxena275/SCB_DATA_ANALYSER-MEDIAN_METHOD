from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://posoco.in/login")

# Fill in form
driver.find_element(By.NAME, "email").send_keys("your_username")
driver.find_element(By.NAME, "password").send_keys("your_password")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

time.sleep(3)

# Navigate to data page
driver.get("https://posoco.in/data")
print(driver.page_source)
