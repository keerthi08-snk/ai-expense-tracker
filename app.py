import os
import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

CREATOR = "S. Keerthi"
COLLEGE = "Kumaraguru College of Technology"
EMAIL = "keerthanaskeerthi97@gmail.com"

# Local demo database
DB_PATH = "/content/project/expenses.db"
os.makedirs("/content/project", exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def setup_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                owner_name TEXT NOT NULL
            )
        """)


setup_database()

st.title("💰 AI Personal Expense Tracker")
st.caption(f"Created by: {CREATOR}")
st.caption(f"College: {COLLEGE}")
st.caption(f"Email: {EMAIL}")
st.divider()

if "profile_name" not in st.session_state:
    st.session_state.profile_name = ""

with st.sidebar:
    st.header("Your Profile")
    profile_name = st.text_input(
        "Enter your name",
        value=st.session_state.profile_name,
        max_chars=60
    ).strip()

    if profile_name:
        st.session_state.profile_name = profile_name

if not profile_name:
    st.info("Enter your name in the sidebar to continue.")
    st.stop()

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Add Expense", "📋 Expense History"]
)

if page == "➕ Add Expense":
    st.header("➕ Add Expense")

    with st.form("expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date", value=date.today())
        description = st.text_input("Expense name")
        category = st.selectbox(
            "Category",
            [
                "Food", "Travel", "Education", "Shopping",
                "Bills", "Health", "Entertainment", "Other"
            ]
        )
        amount = st.number_input(
            "Amount (₹)", min_value=0.01, value=100.0, step=10.0
        )
        submitted = st.form_submit_button("Save Expense")

        if submitted:
            if not description.strip():
                st.error("Please enter an expense name.")
            else:
                with get_connection() as conn:
                    conn.execute("""
                        INSERT INTO expenses
                        (expense_date, description, category, amount, owner_name)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        expense_date.isoformat(),
                        description.strip(),
                        category,
                        amount,
                        profile_name
                    ))
                st.success("Expense saved successfully!")

elif page == "📋 Expense History":
    st.header("📋 Expense History")

    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT expense_date AS Date,
                   description AS Expense,
                   category AS Category,
                   amount AS Amount
            FROM expenses
            WHERE owner_name = ?
            ORDER BY expense_date DESC
        """, conn, params=(profile_name,))

    if df.empty:
        st.info("No expenses yet. Choose Add Expense.")
    else:
        df["Amount"] = df["Amount"].map(lambda x: f"₹{x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.header("📊 Spending Dashboard")

    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT expense_date, description, category, amount
            FROM expenses
            WHERE owner_name = ?
            ORDER BY expense_date
        """, conn, params=(profile_name,))

    if df.empty:
        st.info("No expenses recorded yet. Choose Add Expense.")
    else:
        total = float(df["amount"].sum())
        count = len(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spending", f"₹{total:,.2f}")
        col2.metric("Number of Expenses", count)
        col3.metric("Average Expense", f"₹{total / count:,.2f}")
