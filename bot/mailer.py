"""-1 день в 23:30 каждый день + напоминание"""
import bot.db.crud.users as crud_users
from bot.bot import bot


async def minus_days():
    all_users = crud_users.get_all_users()
    for user in all_users:
        if user.status == 1 and user.days == 2:
            await bot.send_message(
                chat_id=user.chat_id,
                text="Ваша подписка на бота закончится завтра, можете ее приобрести еще раз через /payload"
            )
        if user.status == 1 and user.days == 1:
            await bot.send_message(
                chat_id=user.chat_id,
                text="Ваша подписка на бота закончилась, можете ее приобрести еще раз через /payload"
            )
            crud_users.change_status(user.user_id, 0)
            crud_users.change_days(user.user_id, 0)

    crud_users.minus_day()
