
# 📈 Investment Portfolio Manager

A web-based application built with **Streamlit**, **PostgreSQL**, and **YFinance** that lets users search, track, buy, and sell stocks in a simulated portfolio. It supports **multi-user authentication**, **index tracking**, and more — all in a clean and interactive interface.

---

## 🚀 Features

- 🔐 **User Authentication** (Register & Login)
- 🛒 **Add Stocks to Portfolio** using live YFinance data
- 💼 **Sell Holdings** with PnL tracking
- 📊 **Real-Time Index Ticker** (NIFTY, BankNIFTY, SENSEX, etc.)
- ☁️ **PostgreSQL Integration** for persistent storage

---

## 📁 Folder Structure

```text
portfolio_manager/
│
├── main.py                  # Main app (user dashboard)
├── auth.py                  # Login, registration, authentication
├── database.py              # Database setup and helpers
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (DB credentials)
└── README.md                # This file
```

---

## ⚙️ Tech Stack

| Layer         | Tool                |
|---------------|---------------------|
| Backend       | Python              |
| Web UI        | Streamlit           |
| Database      | PostgreSQL          |
| Stock Data    | YFinance API        |
| News Scraper  | BeautifulSoup       |
| Auth Security | bcrypt hashing      |
| Hosting       | Render / Localhost  |

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/portfolio-manager.git
cd portfolio-manager
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup `.env` File

```env
DB_HOST=your_postgresql_url
```

Example for `DB_HOST`:
```
postgresql://user:pass@host:port/dbname
```

### 5. Create Tables in PostgreSQL

```sql
-- users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- portfolios table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol TEXT,
    company_name TEXT,
    quantity FLOAT,
    buy_price FLOAT,
    buy_date DATE
);

-- sales table
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol TEXT,
    company_name TEXT,
    quantity FLOAT,
    buy_price FLOAT,
    sell_price FLOAT,
    sell_date DATE,
    pnl FLOAT
);
```

### 6. Run the App

#### 🧑 User Dashboard

```bash
streamlit run main.py
```

#### 🧑‍💼 Admin Dashboard

```bash
streamlit run admin.py
```

## 🛡️ Security Notes

- Passwords are hashed with **bcrypt**
- No sensitive data stored in frontend
- PostgreSQL enforces user-linked access

---

## 📦 To-Do / Improvements

- [ ] Add Google Sign-in
- [ ] Integrate real broker APIs (Zerodha, Upstox)
- [ ] Support for Mutual Funds and ETFs
- [ ] Advanced visualizations with Plotly
- [ ] Responsive mobile view

---

## 🧑‍💻 Author

**Vihan Singh Rathore**  
[LinkedIn](https://www.linkedin.com/in/vihansr/) | [GitHub](https://github.com/vihansr)

---

## 📄 License

MIT License. You are free to use and modify this project with credit.
