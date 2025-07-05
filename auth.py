import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(os.getenv("DB_HOST"))


def create_user(username, password, email):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Check for existing username or email
        cur.execute("SELECT 1 FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            return False

        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed))
        conn.commit()
        return True
    except Exception as e:
        print("Error creating user:", e)
        return False
    finally:
        cur.close()
        conn.close()




def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        user_id, hashed = result
        if bcrypt.checkpw(password.encode(), hashed.encode()):
            return user_id
    return None
