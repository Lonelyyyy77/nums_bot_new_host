import sqlite3

from bot.database.db import DB_NAME


def save_user_to_db(user_id, name, username, phone_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO users (user_id, name, username, phone)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET phone=excluded.phone
        """, (user_id, name, username, phone_number))

    conn.commit()
    conn.close()


def get_user_from_db(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, username, phone, code FROM users WHERE user_id = ?
    """, (user_id,))
    user_data = cursor.fetchone()

    conn.close()
    return user_data


def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, username, phone FROM users")  # Выбираем ТОЛЬКО 4 поля
    users = cursor.fetchall()
    conn.close()
    return users



def save_code_to_db(user_id, code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET code = ? WHERE user_id = ?
    """, (code, user_id))

    conn.commit()
    conn.close()


def get_user_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()
    return count

