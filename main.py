import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import yfinance as yf
import psycopg2
import datetime
load_dotenv()

from auth import create_user, login_user

if "user_id" not in st.session_state:
    st.session_state.user_id = None

def show_login_page():
    st.title("Login to Your Portfolio")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        uname = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            user_id = login_user(uname, pwd)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_email = st.text_input("Email", key="reg_email")
        new_pwd = st.text_input("Choose Password", type="password", key="reg_pwd")

        if st.button("Register"):
            if not new_user or not new_email or not new_pwd:
                st.warning("Please fill all fields.")
            else:
                registered = create_user(new_user, new_pwd, new_email)
                if registered:
                    st.success("Registered successfully! Please login.")
                else:
                    st.error("Username or email already exists.")


if st.session_state.user_id is None:
    show_login_page()
    st.stop()


# PostgreSQL Insert
def insert_investment(user_id, symbol, company_name, quantity, buy_price):
    try:
        conn = psycopg2.connect(dsn=os.getenv("DB_HOST"))
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO portfolios (user_id, symbol, company_name, quantity, buy_price, buy_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, symbol, company_name, quantity, buy_price, datetime.date.today()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting into DB: {e}")
        return False

# PostgreSQL Fetch
def fetch_portfolio(user_id):
    try:
        conn = psycopg2.connect(dsn=os.getenv("DB_HOST"))
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, company_name, quantity, buy_price, buy_date
            FROM portfolios
            WHERE user_id = %s
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=["Symbol", "Company", "Quantity", "Buy Price", "Buy Date"])
        return df
    except Exception as e:
        print("Fetch error:", e)
        return pd.DataFrame()

# NSE Ticker List
@st.cache_data
def load_nse_stock_list():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    df["symbol"] = df["SYMBOL"] + ".NS"
    df["display"] = df["symbol"] + " - " + df["NAME OF COMPANY"]
    return df[["symbol", "NAME OF COMPANY", "display"]]

stock_df = load_nse_stock_list()

# UI Starts
st.set_page_config(page_title="Investment Portfolio", layout="wide")
st.title("Welcome to your Investment Portfolio!")
st.markdown("---")

# User placeholder
user_id = st.session_state.user_id

# Portfolio Overview
st.subheader("📊 Your Portfolio Overview")

portfolio_df = fetch_portfolio(user_id)

if not portfolio_df.empty:
    symbols = portfolio_df["Symbol"].unique().tolist()

    # Fetch current prices using yfinance
    tickers = yf.Tickers(" ".join(symbols))
    price_map = {}
    for sym in symbols:
        try:
            price_map[sym] = tickers.tickers[sym].info.get("currentPrice", 0)
        except:
            price_map[sym] = 0

    # Add current price and gain/loss
    portfolio_df["Current Price"] = portfolio_df["Symbol"].map(price_map)
    portfolio_df["Invested Amount"] = portfolio_df["Buy Price"] * portfolio_df["Quantity"]
    portfolio_df["Current Value"] = portfolio_df["Current Price"] * portfolio_df["Quantity"]
    portfolio_df["Unrealized P&L"] = portfolio_df["Current Value"] - portfolio_df["Invested Amount"]

    total_invested = portfolio_df["Invested Amount"].sum()
    total_value = portfolio_df["Current Value"].sum()
    total_gain = portfolio_df["Unrealized P&L"].sum()

    # Summary Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested", f"₹{total_invested:,.0f}")
    col2.metric("Current Value", f"₹{total_value:,.0f}", delta=f"₹{total_gain:,.0f}")
    col3.metric("Profit/Loss (%)", f"{(total_gain / total_invested * 100):.2f}%" if total_invested > 0 else "0%")

    st.dataframe(portfolio_df[
        ["Symbol", "Company", "Quantity", "Buy Price", "Current Price", "Invested Amount", "Current Value", "Unrealized P&L"]
    ].round(2), use_container_width=True)
else:
    st.info("No investments yet. Add one above to get started!")
st.markdown("---")

# Search + Add Section
st.subheader("➕ Add New Investments")
query = st.text_input("Search stock symbol or company name")

if query:
    matches = stock_df[
        stock_df["symbol"].str.contains(query.upper()) |
        stock_df["NAME OF COMPANY"].str.contains(query, case=False)
    ].head(10)

    if not matches.empty:
        choice = st.selectbox("Select stock", matches["display"])
        selected_row = matches[matches["display"] == choice].iloc[0]
        selected_symbol = selected_row["symbol"]
        company_name = selected_row["NAME OF COMPANY"]

        # Fetch from yfinance
        ticker = yf.Ticker(selected_symbol)
        info = ticker.info
        current_price = info.get("currentPrice", "N/A")

        st.write(f"📊 {company_name} ({selected_symbol}) — Current Price: ₹{current_price}")

        with st.form("add_form"):
            quantity = st.number_input("Quantity", min_value=1)
            buy_price = st.number_input("Buy Price (₹)", min_value=0.0, value=current_price if isinstance(current_price, (int, float)) else 0.0)
            submit = st.form_submit_button("💾 Add to Portfolio")

            if submit:
                success = insert_investment(user_id, selected_symbol, company_name, quantity, buy_price)
                if success:
                    st.success("Investment added!")
                else:
                    st.error("Failed to add investment.")
    else:
        st.warning("No matches found.")

st.markdown("---")

st.subheader("📤 Sell Investment")

# Load user's current holdings
portfolio_df = fetch_portfolio(user_id)

if not portfolio_df.empty:
    symbols = portfolio_df["Symbol"].unique().tolist()
    selected_to_sell = st.selectbox("Select stock to sell", symbols)

    stock_row = portfolio_df[portfolio_df["Symbol"] == selected_to_sell].iloc[0]
    max_qty = stock_row["Quantity"]
    buy_price = stock_row["Buy Price"]

    with st.form("sell_form"):
        sell_qty = st.number_input("Quantity to Sell", min_value=1)
        sell_price = st.number_input("Sell Price (₹)", min_value=0.0)
        sell_btn = st.form_submit_button("Sell")

        if sell_btn:
            remaining_qty = max_qty - sell_qty
            realized_pnl = (sell_price - buy_price) * sell_qty
            sell_date = datetime.date.today()

            try:
                conn = psycopg2.connect(os.getenv("DB_HOST"))
                cur = conn.cursor()

                # Insert sale record
                cur.execute("""
                    INSERT INTO sales (user_id, symbol, company_name, quantity, buy_price, sell_price, pnl, sell_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, selected_to_sell, stock_row["Company"], sell_qty,
                    buy_price, sell_price, realized_pnl, sell_date
                ))

                if remaining_qty == 0:
                    # Remove from portfolio
                    cur.execute("""
                        DELETE FROM portfolios
                        WHERE user_id = %s AND symbol = %s
                    """, (user_id, selected_to_sell))
                else:
                    # Update remaining quantity
                    cur.execute("""
                        UPDATE portfolios
                        SET quantity = %s
                        WHERE user_id = %s AND symbol = %s
                    """, (remaining_qty, user_id, selected_to_sell))

                conn.commit()
                cur.close()
                conn.close()

                st.success(f"✅ Sold {sell_qty} of {selected_to_sell} @ ₹{sell_price}")
                st.info(f"💰 Realized P&L: ₹{realized_pnl:,.2f}")

            except Exception as e:
                st.error(f"Sell failed: {e}")
