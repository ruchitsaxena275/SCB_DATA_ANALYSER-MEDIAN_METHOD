import streamlit as st
import requests
import time

st.title("POSOCO Portal Webpage Monitor (Login Required)")

login_url = st.text_input("Login Page URL", "https://yourportal.com/login")
data_url = st.text_input("Data Page URL", "https://yourportal.com/data")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
interval = st.slider("Check interval (seconds)", min_value=30, max_value=600, value=60)
run_monitor = st.button("Start Monitoring")

if "last_seen" not in st.session_state:
    st.session_state["last_seen"] = ""

def login_and_fetch(session, login_url, data_url, username, password):
    payload = {
        'username': username,    # replace with actual field names
        'password': password     # replace with actual field names
    }
    # Log in to the portal
    login_resp = session.post(login_url, data=payload)
    # After login, access the protected page
    data_resp = session.get(data_url)
    return data_resp.text

if run_monitor:
    st.write("Monitoring started. Do not close this browser tab.")
    session = requests.Session()
    while True:
        try:
            content = login_and_fetch(session, login_url, data_url, username, password)
            last_seen = st.session_state["last_seen"]
            if last_seen and last_seen != content:
                st.toast("🔔 New update detected on POSOCO NRDC portal!", icon="⚡")
                st.session_state["last_seen"] = content
                st.write("New update detected at", time.strftime("%Y-%m-%d %H:%M:%S"))
            elif not last_seen:
                st.session_state["last_seen"] = content
        except Exception as e:
            st.error(f"Error: {e}")
        time.sleep(interval)
else:
    st.write("Press 'Start Monitoring' to begin.")

