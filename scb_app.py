import streamlit as st
import requests
import time

st.title("POSOCO Portal Webpage Monitor (Login Required)")

login_url = st.text_input("Login Page URL", "https://posoco.in/login")
data_url = st.text_input("Data Page URL", "https://posoco.in/data")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
interval = st.slider("Check interval (seconds)", 30, 600, 60)
run_monitor = st.button("Start Monitoring")

if "last_seen" not in st.session_state:
    st.session_state["last_seen"] = ""

def login_and_fetch(session, login_url, data_url, username, password):
    payload = {
        "email": username,    # correct field name from HTML
        "password": password
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": login_url,
    }
    # Log in
    login_resp = session.post(login_url, data=payload, headers=headers)
    if login_resp.status_code != 200:
        raise Exception(f"Login failed: {login_resp.status_code}")

    # Fetch data
    data_resp = session.get(data_url, headers=headers)
    if data_resp.status_code != 200:
        raise Exception(f"Data fetch failed: {data_resp.status_code}")
    return data_resp.text

if run_monitor:
    st.write("Monitoring started. Do not close this browser tab.")
    session = requests.Session()
    try:
        content = login_and_fetch(session, login_url, data_url, username, password)
        last_seen = st.session_state["last_seen"]

        if last_seen and last_seen != content:
            st.toast("🔔 New update detected on POSOCO portal!", icon="⚡")
            st.session_state["last_seen"] = content
            st.write("New update detected at", time.strftime("%Y-%m-%d %H:%M:%S"))
        elif not last_seen:
            st.session_state["last_seen"] = content
            st.success("First content fetched successfully.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.write("Press 'Start Monitoring' to begin.")
