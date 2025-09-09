import streamlit as st
import time
import requests
from bs4 import BeautifulSoup

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="POSOCO Alert Monitor", layout="wide")

# ---------------- UI ----------------
st.title("🔍 POSOCO Alert Monitoring Dashboard")

st.sidebar.header("Portal Settings")
portal_url = st.sidebar.text_input("Portal URL", "https://example.com/posoco")  # Replace default
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
check_interval = st.sidebar.number_input("Check Interval (seconds)", min_value=60, value=300)

start_button = st.sidebar.button("🚀 Start Monitoring")

status_placeholder = st.empty()
alert_placeholder = st.empty()

# ---------------- SCRAPING FUNCTION ----------------
def fetch_alert():
    """Fetch the latest code and message from the POSOCO portal."""
    try:
        # Simple GET request (Update this to handle login if required)
        r = requests.get(portal_url, timeout=10, verify=False)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        first_row = soup.select_one("table tbody tr")
        if not first_row:
            return None, None

        code = first_row.select_one("td:nth-child(4)").get_text(strip=True)
        msg = first_row.select_one("td:nth-child(5)").get_text(strip=True)
        return code, msg
    except Exception as e:
        return None, str(e)

# ---------------- MAIN LOGIC ----------------
if start_button:
    st.success("Monitoring started! Leave this tab open.")
    last_code = None

    while True:
        code, msg = fetch_alert()

        if code and msg:
            if code != last_code:
                last_code = code
                alert_placeholder.warning(f"🔔 **New Alert:** {code} - {msg}")
            else:
                status_placeholder.info("✅ No new messages.")
        else:
            status_placeholder.error(f"⚠️ Error fetching data: {msg}")

        time.sleep(check_interval)
