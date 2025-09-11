import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="POSOCO Portal Monitor", layout="wide")
st.title("🔎 POSOCO Portal Webpage Monitor (Login Required)")

# --- Inputs ---
login_url = st.text_input("Login Page URL", "https://posoco.in/login")
data_url = st.text_input("Data Page URL", "https://posoco.in/data")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
interval = st.slider("Refresh interval (seconds)", 30, 600, 60)

# --- Session state ---
if "last_seen" not in st.session_state:
    st.session_state["last_seen"] = ""
if "session" not in st.session_state:
    st.session_state["session"] = requests.Session()
if "monitoring" not in st.session_state:
    st.session_state["monitoring"] = False

def login_and_fetch():
    session = st.session_state["session"]

    # Step 1: GET login page
    resp = session.get(login_url)
    if resp.status_code != 200:
        raise Exception(f"Login page not reachable (HTTP {resp.status_code})")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Step 2: Build payload with hidden fields (CSRF etc.)
    payload = {}
    for hidden in soup.find_all("input", {"type": "hidden"}):
        if hidden.get("name"):
            payload[hidden["name"]] = hidden.get("value", "")

    # Step 3: Add username + password
    payload["email"] = username
    payload["password"] = password

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": login_url,
    }

    # Step 4: POST login
    login_resp = session.post(login_url, data=payload, headers=headers)
    if login_resp.status_code != 200:
        raise Exception(f"Login failed (HTTP {login_resp.status_code})")

    # Step 5: Access data page
    data_resp = session.get(data_url, headers=headers)
    if data_resp.status_code != 200:
        raise Exception(f"Data fetch failed (HTTP {data_resp.status_code})")

    return data_resp.text

# --- Start Monitoring ---
if st.button("Start Monitoring"):
    st.session_state["monitoring"] = True

if st.session_state["monitoring"]:
    try:
        content = login_and_fetch()
        last_seen = st.session_state["last_seen"]

        if last_seen and last_seen != content:
            st.toast("🔔 New update detected on POSOCO portal!", icon="⚡")
            st.write("✅ Update detected at", time.strftime("%Y-%m-%d %H:%M:%S"))
        elif not last_seen:
            st.success("✅ First fetch successful, monitoring started.")

        st.session_state["last_seen"] = content

    except Exception as e:
        st.error(f"❌ Error: {e}")

    # Auto-refresh
    time.sleep(interval)
    st.experimental_rerun()
