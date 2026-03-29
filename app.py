import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="PragyanAI AI BI Dashboard", layout="wide")
st.image("PragyanAI_Transperent.png")

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")
conn.commit()

# -----------------------------
# AUTH FUNCTIONS
# -----------------------------
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def register_user(username, password):
    c.execute("INSERT INTO users VALUES (?,?)", (username, password))
    conn.commit()

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if not st.session_state.logged_in:

    if choice == "Login":
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.success("✅ Logged in successfully")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    elif choice == "Register":
        st.title("Register")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Register"):
            register_user(new_user, new_pass)
            st.success("✅ Account created")
else:

    # -----------------------------
    # LOAD DATA (REAL-TIME SIMULATION)
    # -----------------------------
    @st.cache_data(ttl=10)
    def load_data():
        url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
        df = pd.read_csv(url)

        # Add fake date column
        df["date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="D")
        return df

    df = load_data()

    st.title("AI Tableau-Style Dashboard")
