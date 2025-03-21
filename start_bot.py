import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
import dotenv

from bot.database.db import init_db
from bot.routers.routers import start_router, user_routers, admin_routers

dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
TEST_ID = os.getenv('TEST_ID')

test_id = TEST_ID
admin_id = OWNER_ID

router = Router()
bot = Bot(token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)


async def main():
    dp = Dispatcher()

    await start_router(dp)
    await user_routers(dp)
    await admin_routers(dp)

    init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Interrupted by user...")