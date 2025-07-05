import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv("DB_HOST")

conn = psycopg2.connect(dsn=DB_HOST)
cur = conn.cursor()

cur.execute("""
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INT,
    symbol VARCHAR(20),
    company_name TEXT,
    quantity FLOAT,
    buy_price FLOAT,
    buy_date DATE DEFAULT CURRENT_DATE
);
""")

cur.execute("""
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    quantity FLOAT NOT NULL,
    buy_price FLOAT NOT NULL,
    sell_price FLOAT NOT NULL,
    sell_date DATE DEFAULT CURRENT_DATE,
    pnl FLOAT NOT NULL
);

""")

cur.execute("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

""")

conn.commit()
cur.close()
conn.close()
