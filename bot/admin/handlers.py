from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import bot.admin.texts as texts
import bot.admin.keyboards as keyboards

import bot.db.crud.users as crud_users
from bot.db.models.users import Users as Users

from bot.bot import bot
import config

router = Router()


@router.message(Command("admin"))
async def admin(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
        await state.clear()
    except:
        ...
    user_id = int(message.from_user.id)
    if user_id not in config.admins:
        return await message.answer(
            text=texts.no_access,
            reply_markup=keyboards.back_menu_keyboard
        )
    await message.answer(
        text=texts.admin_text,
        reply_markup=keyboards.admin_keyboard
    )


@router.callback_query(F.data == "admin")
async def admin_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.edit_reply_markup()
        await state.clear()
    except:
        ...
    user_id = int(callback.from_user.id)
    if user_id not in config.admins:
        return await callback.message.answer(
            text=texts.no_access,
            reply_markup=keyboards.back_menu_keyboard
        )
    await callback.message.answer(
        text=texts.admin_text,
        reply_markup=keyboards.admin_keyboard
    )


@router.callback_query(F.data == "watch_users")
async def watch_users(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    s = "Список пользователей бота:\n"
    users = crud_users.get_all_users()
    count = 0
    for user in users:
        count += 1
        s += f"{count}) {user.user_id} - {user.username}\n"

    await callback.message.answer(s, reply_markup=keyboards.admin_back_menu_keyboard)


@router.callback_query(F.data == "watch_white_users")
async def watch_users(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    s = "Список пользователей бота с подпиской:\n"
    users = crud_users.get_all_users()
    count = 0
    for user in users:
        if user.status == 1:
            count += 1
            s += f"{count}) {user.user_id} - {user.username}\n"

    await callback.message.answer(s, reply_markup=keyboards.admin_back_menu_keyboard)


class Issue(StatesGroup):
    user_id = State()
    username = State()
    days = State()


@router.callback_query(F.data == "issue_subscription")
async def issue_subscription(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(
        text="Введите id пользователя",
        reply_markup=keyboards.admin_back_menu_keyboard
    )
    await state.set_state(Issue.user_id)


@router.message(Issue.user_id)
async def issue_user_id(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...

    user_id = message.text
    try:
        user_id = int(user_id)
    except:
        return await message.answer(
            text="введите номерной id",
            reply_markup=keyboards.admin_back_menu_keyboard
        )
    await state.update_data({"user_id": user_id})
    await message.answer(
        text="введите username пользователя(ник через @) без собачки, если его нет, напишите None",
        reply_markup=keyboards.admin_back_menu_keyboard
    )
    await state.set_state(Issue.username)


@router.message(Issue.username)
async def issue_username(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    username = message.text
    await state.update_data({"username": username})
    await message.answer(
        text="введите количество дней для подписки",
        reply_markup=keyboards.admin_back_menu_keyboard
    )
    await state.set_state(Issue.days)


@router.message(Issue.days)
async def issue_username(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...

    days = message.text
    try:
        days = int(days)
    except:
        return await message.answer(
            text="Введите валидное число",
            reply_markup=keyboards.admin_back_menu_keyboard
        )

    data = await state.get_data()
    user = Users(user_id=int(data["user_id"]),
                 username=data["username"] if data["username"] != "None" else "None", status=1,
                 days=days)
    crud_users.add_user(user)
    await message.answer(
        text="Пользователю выдана подписка",
        reply_markup=keyboards.admin_back_menu_keyboard
    )
