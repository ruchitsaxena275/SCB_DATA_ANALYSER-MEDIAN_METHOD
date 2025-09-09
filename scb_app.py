import streamlit as st
import time
import requests
from bs4 import BeautifulSoup

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="POSOCO Alert Monitor", layout="wide")

# ---------------- UI ----------------
st.title("🔍 POSOCO Alert Monitoring Dashboard")

st.sidebar.header("Portal Settings")
login_url = st.sidebar.text_input("Login URL", "https://example.com/login")  # Replace with POSOCO login URL
data_url = st.sidebar.text_input("Data URL", "https://example.com/data")    # Replace with POSOCO data page
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
check_interval = st.sidebar.number_input("Check Interval (seconds)", min_value=60, value=300)
run_monitor = st.sidebar.checkbox("Start Monitoring")

status_placeholder = st.empty()
alert_placeholder = st.empty()

# ---------------- LOGIN FUNCTION ----------------
def login_and_get_session():
    """
    Logs into POSOCO and returns a requests.Session object.
    Adjust 'payload' keys based on actual HTML form field names.
    """
    session = requests.Session()
    try:
        # Adjust these field names to match your login form
        payload = {
            "username": username,
            "password": password
        }
        r = session.post(login_url, data=payload, timeout=10, verify=False)
        r.raise_for_status()
        return session
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

# ---------------- SCRAPING FUNCTION ----------------
def fetch_alert(session):
    """Fetch latest alert from POSOCO data page using logged-in session."""
    try:
        r = session.get(data_url, timeout=10, verify=False)
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

# ---------------- MAIN LOOP ----------------
if run_monitor:
    if not username or not password:
        st.error("⚠️ Please enter username and password in the sidebar.")
    else:
        st.success("🔑 Logging in...")
        session = login_and_get_session()

        if session:
            st.success("✅ Login successful! Monitoring started.")
            last_code = None

            while run_monitor:
                code, msg = fetch_alert(session)

                if code and msg:
                    if code != last_code:
                        last_code = code
                        alert_placeholder.warning(f"🔔 **New Alert:** {code} - {msg}")
                    else:
                        status_placeholder.info("✅ No new messages.")
                else:
                    status_placeholder.error(f"⚠️ Error fetching data: {msg}")

                time.sleep(check_interval)
                st.experimental_rerun()
