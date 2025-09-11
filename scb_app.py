import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="POSOCO Alert Monitor", layout="wide")
st.title("🔍 POSOCO Alert Monitoring Dashboard")

st.sidebar.header("Portal Settings")
login_url = st.sidebar.text_input("Login URL", "https://oms.nrlcd.in/")  # Replace with actual
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
check_interval = st.sidebar.number_input("Check Interval (seconds)", min_value=60, value=300)
run_monitor = st.sidebar.checkbox("Start Monitoring")

status_placeholder = st.empty()
alert_placeholder = st.empty()

def login_and_get_page():
    """Use Selenium to log in and fetch the page HTML."""
    status_placeholder.info("🔑 Logging in...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
   options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get(login_url)
    time.sleep(3)  # wait for page load

    # Adjust selectors based on actual HTML form
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

def extract_alert(html):
    """Extract the latest alert message from page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    first_row = soup.select_one("table tbody tr")
    if not first_row:
        return None, None
    code = first_row.select_one("td:nth-child(4)").get_text(strip=True)
    msg = first_row.select_one("td:nth-child(5)").get_text(strip=True)
    return code, msg

if run_monitor:
    last_code = None
    while run_monitor:
        try:
            html = login_and_get_page()
            code, msg = extract_alert(html)

            if code and msg:
                if code != last_code:
                    alert_placeholder.warning(f"🔔 **New Alert:** {code} - {msg}")
                    last_code = code
                else:
                    status_placeholder.info("✅ No new messages.")
            else:
                status_placeholder.error("⚠️ No alerts found.")
        except Exception as e:
            status_placeholder.error(f"Login failed: {e}")

        time.sleep(check_interval)
        st.experimental_rerun()



