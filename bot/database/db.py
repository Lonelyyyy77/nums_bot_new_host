import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        username TEXT,
        phone TEXT,
        code TEXT,
        two_fa_disabled INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()