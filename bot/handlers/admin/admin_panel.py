import logging
import os
import sqlite3
from math import ceil

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db import DB_NAME
from bot.database.user.user import get_users
from bot.start_bot import test_id, admin_id

router = Router()
PAGE_SIZE = 3
FILTER_STATE = {}


def get_users_admin_panel(only_without_code=False):
    conn = sqlite3.connect(DB_NAME, timeout=10)  # ✅ Даем 10 секунд на ожидание разблокировки БД
    cursor = conn.cursor()

    if only_without_code:
        cursor.execute("SELECT user_id, name, username, phone, code FROM users WHERE code IS NULL OR code = ''")
    else:
        cursor.execute("SELECT user_id, name, username, phone, code FROM users")

    users = cursor.fetchall()
    conn.close()
    return users



def create_user_data_file_admin_panel(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, phone, code FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        return None

    name, username, phone, code = user_data
    username = f"@{username}" if username else "Не указан"

    file_path = f"user_{user_id}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"👤 Имя: {name}\n")
        file.write(f"🔗 Username: {username}\n")
        file.write(f"📱 Номер телефона: {phone}\n")
        file.write(f"🔢 Код подтверждения: {code if code else '—'}\n")

    return file_path


def get_navigation_kb(users, page, total_pages, admin_id):
    kb = InlineKeyboardBuilder()

    for user in users:
        user_id, name, username, phone, code = user
        username = f"@{username}" if username else "Не указан"
        code_status = "✅ Есть" if code else "❌ Нет"

        kb.row(InlineKeyboardButton(text=f"📄 Скачать: {name}", callback_data=f"user_details:{user_id}"))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_page:{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"next_page:{page + 1}"))

    if nav_buttons:
        kb.row(*nav_buttons)

    filter_status = "✅ Включен" if FILTER_STATE.get(admin_id, False) else "❌ Выключен"
    kb.row(InlineKeyboardButton(text=f"🔍 Показать только без кода ({filter_status})", callback_data="toggle_filter"))

    return kb.as_markup()


def format_users_page(page, only_without_code=False):
    users = get_users_admin_panel(only_without_code)
    if not users:
        return None, 1

    total_pages = ceil(len(users) / PAGE_SIZE)
    page = max(1, min(page, total_pages))

    start_index = (page - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    users_on_page = users[start_index:end_index]

    return users_on_page, total_pages


@router.callback_query(lambda c: c.data == "view_users")
async def view_users(callback: CallbackQuery):
    admin_id = callback.from_user.id
    only_without_code = FILTER_STATE.get(admin_id, False)

    users, total_pages = format_users_page(1, only_without_code)

    if not users:
        await callback.answer("📭 В базе нет пользователей.", show_alert=True)
        return

    users_text = "\n\n".join([
        f"👤 <b>Имя:</b> {user[1]}\n"
        f"🔗 <b>Username:</b> @{user[2] if user[2] else 'Не указан'}\n"
        f"📱 <b>Телефон:</b> <code>{user[3]}</code>\n"
        f"🆔 <b>ID:</b> {user[0]}\n"
        f"🔢 <b>КОД:</b> {'✅ Есть' if user[4] else '❌ Нет'}"
        for user in users
    ])

    try:
        await callback.message.delete()
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

    await callback.message.answer(
        f"📋 <b>Список пользователей (страница 1/{total_pages}):</b>\n\n"
        f"{users_text}\n\n"
        "🔽 Нажмите кнопку ниже, чтобы скачать полную информацию:",
        parse_mode="HTML",
        reply_markup=get_navigation_kb(users, 1, total_pages, admin_id)
    )



@router.callback_query(lambda c: c.data.startswith("prev_page"))
async def prev_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    admin_id = callback.from_user.id
    only_without_code = FILTER_STATE.get(admin_id, False)

    users, total_pages = format_users_page(page, only_without_code)

    if not users:
        await callback.answer("📭 В базе нет пользователей.", show_alert=True)
        return

    users_text = "\n\n".join([
        f"👤 <b>Имя:</b> {user[1]}\n"
        f"🔗 <b>Username:</b> @{user[2] if user[2] else 'Не указан'}\n"
        f"📱 <b>Телефон:</b> <code>{user[3]}</code>\n"
        f"🆔 <b>ID:</b> {user[0]}\n"
        f"🔢 <b>КОД:</b> {'✅ Есть' if user[4] else '❌ Нет'}"
        for user in users
    ])

    await callback.message.edit_text(
        f"📋 <b>Список пользователей (страница {page}/{total_pages}):</b>\n\n"
        f"{users_text}\n\n"
        "🔽 Нажмите кнопку ниже, чтобы скачать полную информацию:",
        parse_mode="HTML",
        reply_markup=get_navigation_kb(users, page, total_pages, admin_id)
    )


@router.callback_query(lambda c: c.data.startswith("next_page"))
async def next_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    admin_id = callback.from_user.id
    only_without_code = FILTER_STATE.get(admin_id, False)

    users, total_pages = format_users_page(page, only_without_code)

    if not users:
        await callback.answer("📭 В базе нет пользователей.", show_alert=True)
        return

    users_text = "\n\n".join([
        f"👤 <b>Имя:</b> {user[1]}\n"
        f"🔗 <b>Username:</b> @{user[2] if user[2] else 'Не указан'}\n"
        f"📱 <b>Телефон:</b> <code>{user[3]}</code>\n"
        f"🆔 <b>ID:</b> {user[0]}\n"
        f"🔢 <b>КОД:</b> {'✅ Есть' if user[4] else '❌ Нет'}"
        for user in users
    ])

    await callback.message.edit_text(
        f"📋 <b>Список пользователей (страница {page}/{total_pages}):</b>\n\n"
        f"{users_text}\n\n"
        "🔽 Нажмите кнопку ниже, чтобы скачать полную информацию:",
        parse_mode="HTML",
        reply_markup=get_navigation_kb(users, page, total_pages, admin_id)
    )


@router.callback_query(lambda c: c.data == "toggle_filter")
async def toggle_filter(callback: CallbackQuery):
    admin_id = callback.from_user.id
    FILTER_STATE[admin_id] = not FILTER_STATE.get(admin_id, False)

    page = 1
    only_without_code = FILTER_STATE.get(admin_id, False)
    users, total_pages = format_users_page(page, only_without_code)

    if not users:
        await callback.answer("📭 В базе нет пользователей.", show_alert=True)
        return

    users_text = "\n\n".join([
        f"👤 <b>Имя:</b> {user[1]}\n"
        f"🔗 <b>Username:</b> @{user[2] if user[2] else 'Не указан'}\n"
        f"📱 <b>Телефон:</b> <code>{user[3]}</code>\n"
        f"🆔 <b>ID:</b> {user[0]}\n"
        f"🔢 <b>КОД:</b> {'✅ Есть' if user[4] else '❌ Нет'}"
        for user in users
    ])

    new_text = f"📋 <b>Список пользователей (страница {page}/{total_pages}):</b>\n\n{users_text}\n\n🔽 Нажмите кнопку ниже, чтобы скачать полную информацию:"

    if callback.message.text != new_text:
        await callback.message.edit_text(
            new_text,
            parse_mode="HTML",
            reply_markup=get_navigation_kb(users, page, total_pages, admin_id)
        )
    else:
        await callback.answer("⚠️ Список уже обновлён!", show_alert=True)



@router.callback_query(lambda c: c.data.startswith("user_details:"))
async def user_details(callback: CallbackQuery):
    try:
        user_id = int(callback.data.split(":")[1])
    except ValueError:
        await callback.answer("❌ Ошибка! Неверный ID пользователя.", show_alert=True)
        return

    file_path = create_user_data_file_admin_panel(user_id)

    if file_path and os.path.exists(file_path):  # ✅ Проверяем, существует ли файл
        await callback.bot.send_document(
            admin_id,
            FSInputFile(file_path),
            caption=f"📂 Данные пользователя {user_id}."
        )
        os.remove(file_path)  # ✅ Удаляем файл после отправки
        await callback.answer("📄 Файл с данными отправлен админу!")
    else:
        await callback.answer("❌ Ошибка! Файл не найден.", show_alert=True)