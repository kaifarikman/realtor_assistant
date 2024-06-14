from aiogram import Dispatcher

import asyncio
import logging
import sys

from bot.admin.handlers import router as admin_router
from bot.user.handlers import router as user_router
from bot.bot import bot

import bot.db.db as db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import bot.mailer as mailer


async def main():
    db.create_tables()
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    shed = AsyncIOScheduler(timezone='Europe/Moscow')
    shed.add_job(mailer.minus_days, "cron", hour=23, minute=30)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except Exception as exception:
        print(f"Exit - {exception}!")

