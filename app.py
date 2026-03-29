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
    # -----------------------------
    # SIDEBAR FILTERS
    # -----------------------------
    st.sidebar.header("Filters")

    # Date filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df["date"].min(), df["date"].max()]
    )

    # Category filters
    day = st.sidebar.multiselect("Day", df["day"].unique(), default=df["day"].unique())
    time_filter = st.sidebar.multiselect("Time", df["time"].unique(), default=df["time"].unique())

    # -----------------------------
    # APPLY FILTERS
    # -----------------------------
    filtered_df = df[
        (df["day"].isin(day)) &
        (df["time"].isin(time_filter))
    ]

    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df["date"] >= pd.to_datetime(date_range[0])) &
            (filtered_df["date"] <= pd.to_datetime(date_range[1]))
        ]

    # -----------------------------
    # KPIs
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(filtered_df))
    col2.metric("Avg Bill", f"${filtered_df['total_bill'].mean():.2f}")
    col3.metric("Avg Tip", f"${filtered_df['tip'].mean():.2f}")
    
    # -----------------------------
    # DYNAMIC CHART SELECTOR
    # -----------------------------
    st.subheader("Dynamic Chart Builder")

    chart_type = st.selectbox("Select Chart Type", ["Bar", "Line", "Scatter", "Pie"])

    x_axis = st.selectbox("X Axis", filtered_df.columns)
    y_axis = st.selectbox("Y Axis", filtered_df.select_dtypes(include='number').columns)

    if chart_type == "Bar":
        fig = px.bar(filtered_df, x=x_axis, y=y_axis, color="day")
    elif chart_type == "Line":
        fig = px.line(filtered_df, x=x_axis, y=y_axis)
    elif chart_type == "Scatter":
        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color="day")
    elif chart_type == "Pie":
        fig = px.pie(filtered_df, names=x_axis, values=y_axis)

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # AUTO REFRESH (REAL-TIME)
    # -----------------------------
    st.subheader("Real-Time Simulation")

    refresh = st.checkbox("Enable Auto Refresh")

    if refresh:
        st.info("Refreshing every 10 seconds...")
        time.sleep(10)
        st.rerun()
