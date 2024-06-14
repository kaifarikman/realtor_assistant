from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.filters import Command, CommandStart

import bot.user.texts as texts
import bot.user.keyboards as keyboards
import bot.user.utils as utils

import bot.db.crud.users as crud_users
from bot.db.models.users import Users as Users

from bot.bot import bot
import config

import datetime
import re

router = Router()


@router.message(CommandStart())
async def start_(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
        await state.clear()
    except:
        ...
    user_id = int(message.from_user.id)
    user = Users(user_id=user_id,
                 username=message.from_user.username if str(message.from_user.username) != "None" else "None", status=0,
                 days=0, trial_status=0)
    crud_users.add_user(user)

    await message.answer(
        text=texts.start_message,
        reply_markup=keyboards.start_keyboard, parse_mode="HTML"
    )


@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.edit_reply_markup()
        await state.clear()
    except:
        ...
    await callback.message.answer(
        text=texts.start_message,
        reply_markup=keyboards.start_keyboard, parse_mode="HTML"
    )


@router.message(Command("payment"))
async def payment(message: Message):
    user_id = int(message.from_user.id)
    if crud_users.get_user_status(user_id) == 1:
        return await message.answer(
            text=f"До конца подписки осталось: {crud_users.get_user_days(user_id)}дня/дней",
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await bot.send_invoice(
        chat_id=user_id,
        title="Оплата подписки для бота ассистента риелтора",
        description="Оплата подписки",
        payload="realtor_payload",
        provider_token=config.PROVIDER_TOKEN,
        currency="RUB",
        prices=[
            {"label": "Руб", "amount": 500 * 100},  # this is {price}.00
        ],
    )


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id, ok=True
    )


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: Message):
    if message.successful_payment.invoice_payload == "realtor_payload":
        await message.answer(
            text="Вы успешно приобрели подписку на бота на месяц. Теперь вам доступны его функции",
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
        crud_users.change_status(int(message.from_user.id), 1)
        crud_users.change_days(int(message.from_user.id), 31)


@router.callback_query(F.data == "get_trial")
async def get_trial(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_users.get_user_trial(user_id) == 0:
        crud_users.change_status(user_id, 1)
        crud_users.change_days(user_id, 3)
        crud_users.change_trial(user_id, 1)
        return await callback.message.answer(
            text="Вам выдана подписка на 3 дня.",
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await callback.message.answer(
        text="Вы уже приобрели/приобретали данную подписку. Вам она недоступна",
        reply_markup=keyboards.back_keyboard, parse_mode="HTML"
    )


class Mortgage(StatesGroup):
    su = State()
    sr = State()
    st = State()


@router.callback_query(F.data == "mortgage_payment_calculation")
async def payment_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_users.get_user_status(user_id) == 0:
        "не подписан, прописываем подписку"
        return await callback.message.answer(
            text=texts.payment_message,
            reply_markup=keyboards.get_trial, parse_mode="HTML"
        )

    await callback.message.answer(
        text=texts.su, parse_mode="HTML"
    )
    await state.set_state(Mortgage.su)


@router.message(Mortgage.su)
async def su_state(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"su": f"{utils.check_number(number)}"})
    await message.answer(
        text=texts.sr, parse_mode="HTML"
    )
    await state.set_state(Mortgage.sr)


@router.message(Mortgage.sr)
async def st_state(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"sr": f"{utils.check_number(number)}"})
    await message.answer(
        text=texts.st, parse_mode="HTML"
    )
    await state.set_state(Mortgage.st)


@router.message(Mortgage.st)
async def st_state(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    data = await state.get_data()
    await state.clear()
    su_number = float(data["su"])
    sr_number = float(data["sr"])
    st_number = float(utils.check_number(number))
    sr_number_12 = sr_number * 12
    try:
        t = float(sr_number * 12)
        g = float(st_number / 1200)
        for_month = (su_number * g) / (1 - ((g + 1.0) ** (-t)))
        all_time = for_month * t - su_number
    except:
        return await message.answer(
            text=texts.bad_info,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await message.answer(
        text=texts.mortgage_answer_message(
            su_number, sr_number, sr_number_12, st_number,
            for_month, all_time
        ),
        reply_markup=keyboards.back_keyboard,
        parse_mode="HTML"
    )


class Overstatement(StatesGroup):
    real_cost = State()
    amount = State()
    pv = State()


@router.callback_query(F.data == "overstatement_calculator")
async def overstatement_calculator(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.edit_reply_markup()
        await state.clear()
    except:
        ...

    user_id = int(callback.from_user.id)
    if crud_users.get_user_status(user_id) == 0:
        "не подписан, прописываем подписку"
        return await callback.message.answer(
            text=texts.payment_message,
            reply_markup=keyboards.get_trial, parse_mode="HTML"
        )

    await callback.message.answer(
        text=texts.real_cost, parse_mode="HTML"
    )
    await state.set_state(Overstatement.real_cost)


@router.message(Overstatement.real_cost)
async def real_cost_(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"real_cost": f"{utils.check_number(number)}"})
    await message.answer(
        text=texts.amount, parse_mode="HTML"
    )
    await state.set_state(Overstatement.amount)


@router.message(Overstatement.amount)
async def real_cost_(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"amount": f"{utils.check_number(number)}"})
    await message.answer(
        text=texts.pv, parse_mode="HTML"
    )
    await state.set_state(Overstatement.pv)


@router.message(Overstatement.pv)
async def pv_(message: Message, state: FSMContext):
    try:
        await message.edit_reply_markup()
    except:
        ...
    number = str(message.text)
    if utils.check_number(number) == "error":
        return message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    data = await state.get_data()
    real_cost = round(float(data["real_cost"]), 2)
    amount = round(float(data["amount"]), 2)
    pv = round(utils.check_number(number), 2)
    suma = round(real_cost - amount, 2)
    apartment_cost = round(suma / ((100.0 - pv) / 100), 2)
    size_pv = round(apartment_cost - suma, 2)
    receipt = round(size_pv - amount, 2)
    await message.answer(
        text=texts.overstatement(real_cost, amount, pv, apartment_cost,
                                 suma, size_pv, receipt), reply_markup=keyboards.back_keyboard, parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data == "tax_calculator")
async def tax_calculation(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_users.get_user_status(user_id) == 0:
        "не подписан, прописываем подписку"
        return await callback.message.answer(
            text=texts.payment_message,
            reply_markup=keyboards.get_trial, parse_mode="HTML"
        )

    await callback.message.answer(
        text=texts.tax_text,
        reply_markup=keyboards.tax_keyboard, parse_mode="HTML"
    )


class BuySell(StatesGroup):
    date = State()
    buy = State()
    sell = State()
    cadastral = State()


@router.callback_query(F.data == "buysell_calculator")
async def buysell_calculation(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await callback.message.edit_reply_markup()
    except Exception:
        ...
    await callback.message.answer(text=texts.date, parse_mode="HTML")
    await state.set_state(BuySell.date)


@router.message(BuySell.date)
async def buysell_data(message: Message, state: FSMContext):
    msg = message.text
    trying, error = utils.check_date(msg)
    if not trying:
        return await message.answer(text=texts.error_date, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await message.answer(text=texts.price_of, parse_mode="HTML")
    await state.update_data({"date": f"{msg}"})
    await state.set_state(BuySell.buy)


@router.message(BuySell.buy)
async def buysell_buy(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await message.answer(text=texts.cadastral_message, parse_mode="HTML")
    await state.update_data({"buy": utils.check_number(str(msg))})
    await state.set_state(BuySell.cadastral)


@router.message(BuySell.cadastral)
async def buysell_cadastr(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"cadastral": utils.check_number(str(msg))})
    await message.answer(text=texts.price_buy, parse_mode="HTML")
    await state.set_state(BuySell.sell)


@router.message(BuySell.sell)
async def buysell_sell(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"sell": utils.check_number(str(msg))})
    await message.answer(text=texts.question, reply_markup=keyboards.buysell_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "buysell_yes")
async def buysell_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    data = await state.get_data()
    await state.clear()

    date, buy, sell, cadastral = data["date"].split("."), data["buy"], data["sell"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date
    "правки"

    cadastral *= 0.7
    sell = max(sell, cadastral)

    if sell < buy:
        return await callback.message.answer(text="Налога не возникает ✅\nСтоимость продажи меньше суммы покупки",
                                             reply_markup=keyboards.back_keyboard, parse_mode="HTML")
    if int(str(different_date).split()[0]) // 365 < 3:
        await callback.message.answer(text=texts.buysell_false(sell, buy), parse_mode="HTML")
        return await callback.message.answer(text=texts.warning_message, reply_markup=keyboards.back_keyboard,
                                             parse_mode="HTML")
    await callback.message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "buysell_no")
async def buysell_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    data = await state.get_data()
    await state.clear()

    date, buy, sell, cadastral = data["date"].split("."), data["buy"], data["sell"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date
    "правки"

    cadastral *= 0.7
    sell = max(sell, cadastral)

    if sell < buy:
        return await callback.message.answer(
            text="Налога не возникает ✅\nСтоимость продажи меньше суммы покупки\n\nИстек минимальный срок для продажи объекта без НДФЛ ⌛️",
            reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    if int(str(different_date).split()[0]) // 365 < 5:
        await callback.message.answer(text=texts.buysell_false(sell, buy), parse_mode="HTML")
        return await callback.message.answer(text=texts.warning_message, reply_markup=keyboards.back_keyboard,
                                             parse_mode="HTML")
    await callback.message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


class Assignment(StatesGroup):
    calculation = State()
    buy = State()
    sell = State()
    cadastral = State()


@router.callback_query(F.data == "assignment_calculator")
async def assignment_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(text=texts.fact_date, parse_mode="HTML")
    await state.set_state(Assignment.calculation)


@router.message(Assignment.calculation)
async def assignment_buy(message: Message, state: FSMContext):
    msg = message.text

    trying, error = utils.check_date(msg)
    if not trying:
        return await message.answer(text=texts.error_date, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await state.update_data({"assignment": f"{msg}"})
    await message.answer(text=texts.price_object, parse_mode="HTML")
    await state.set_state(Assignment.buy)


@router.message(Assignment.buy)
async def assignment_cost(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"buy": utils.check_number(str(msg))})

    await message.answer(text=texts.cadastral_message, parse_mode="HTML")
    await state.set_state(Assignment.cadastral)


@router.message(Assignment.cadastral)
async def assignment_cadas(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"cadastral": utils.check_number(str(msg))})
    await message.answer(text=texts.object_buy, parse_mode="HTML")
    await state.set_state(Assignment.sell)


@router.message(Assignment.sell)
async def assignment_sold(message: Message, state: FSMContext):
    msg = message.text

    if utils.check_number(str(msg)) == "error":
        return message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"sold": utils.check_number(str(msg))})
    await message.answer(text=texts.question2, reply_markup=keyboards.assignment_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "assignment_yes")
async def assignment_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    data = await state.get_data()
    await state.clear()

    date, buy, sell, cadastral = data["assignment"].split("."), data["buy"], data["sold"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date

    cadastral *= 0.7
    sell = max(sell, cadastral)

    if int(str(different_date).split()[0]) // 365 < 3:
        await callback.message.answer(text=texts.buysell_false(sell, buy), parse_mode="HTML")
        return await callback.message.answer(text=texts.message_for_assigment, reply_markup=keyboards.back_keyboard,
                                             parse_mode="HTML")
    await callback.message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


@router.callback_query(F.data == "assignment_no")
async def assignment_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    data = await state.get_data()
    await state.clear()

    date, buy, sell, cadastral = data["assignment"].split("."), data["buy"], data["sold"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date

    cadastral *= 0.7
    sell = max(sell, cadastral)

    if int(str(different_date).split()[0]) // 365 < 5:
        await callback.message.answer(text=texts.buysell_false(sell, buy), parse_mode="HTML")
        return await callback.message.answer(text=texts.message_for_assigment, reply_markup=keyboards.back_keyboard,
                                             parse_mode="HTML")
    await callback.message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


class Gifting(StatesGroup):
    date = State()
    sell = State()
    cadastral = State()


@router.callback_query(F.data == "gift_calculator")
async def gift_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(text=texts.date, parse_mode="HTML")
    await state.set_state(Gifting.date)


@router.message(Gifting.date)
async def gift_date(message: Message, state: FSMContext):
    msg = message.text
    trying, error = utils.check_date(msg)
    if not trying:
        return await message.answer(text=texts.error_date, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await message.answer(text=texts.cadastral_message, parse_mode="HTML")  # price_buy

    await state.update_data({"date": f"{msg}"})
    await state.set_state(Gifting.cadastral)


@router.message(Gifting.cadastral)
async def gift_cadastral(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"cadastral": utils.check_number(str(msg))})
    await message.answer(text=texts.price_buy, parse_mode="HTML")
    await state.set_state(Gifting.sell)


@router.message(Gifting.sell)
async def gift_sell(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"sold": utils.check_number(str(msg))})
    data = await state.get_data()
    await state.clear()

    date, sell, cadastral = data["date"].split("."), data["sold"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date

    sell = max(sell, cadastral * 0.7)

    if int(str(different_date).split()[0]) // 365 < 3:
        await message.answer(text=texts.gifting_false(sell), parse_mode="HTML")
        return await message.answer(text=texts.prava_message, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    return await message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


class Privatization(StatesGroup):
    date = State()
    sell = State()
    cadastral = State()


@router.callback_query(F.data == "privatization_calculator")
async def privatization_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(text="Дата регистрации права собственности на Объект (в формате ДД.ММ.ГГГГ):",
                                  reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await state.set_state(Privatization.date)


@router.message(Privatization.date)
async def privatization_date(message: Message, state: FSMContext):
    msg = message.text
    trying, error = utils.check_date(msg)
    if not trying:
        error_message = "Вы ввели неверную дату."
        return await message.answer(text=error_message, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await message.answer(text=texts.cadastral_message, parse_mode="HTML")  # "Введите стоимость продажи объекта:"

    await state.update_data({"date": f"{msg}"})
    await state.set_state(Privatization.cadastral)


@router.message(Privatization.cadastral)
async def privatization_cadastral(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"cadastral": utils.check_number(str(msg))})
    await message.answer(text="Введите стоимость продажи объекта:", parse_mode="HTML")
    await state.set_state(Privatization.sell)


@router.message(Privatization.sell)
async def privatization_sell(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"sold": utils.check_number(str(msg))})
    data = await state.get_data()
    await state.clear()

    date, sell, cadastral = data["date"].split("."), data["sold"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date

    sell = max(sell, cadastral * 0.7)

    if int(str(different_date).split()[0]) // 365 < 3:
        await message.answer(text=texts.privatization_false(sell), parse_mode="HTML")
        return await message.answer(text=texts.privat, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


class Heritage(StatesGroup):
    date = State()
    sell = State()
    cadastral = State()


@router.callback_query(F.data == "heritage_calculator")
async def heritage_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    await callback.message.answer(text=texts.death, parse_mode="HTML")
    await state.set_state(Heritage.date)


@router.message(Heritage.date)
async def heritage_data(message: Message, state: FSMContext):
    msg = message.text
    trying, error = utils.check_date(msg)
    if not trying:
        error_message = "Вы ввели неверную дату."
        return await message.answer(text=error_message, reply_markup=keyboards.back_keyboard, parse_mode="HTML")

    await message.answer(text=texts.cadastral_message, parse_mode="HTML")
    await state.update_data({"date": f"{msg}"})
    await state.set_state(Heritage.cadastral)


@router.message(Heritage.cadastral)
async def heritage_cadastral(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"cadastral": utils.check_number(str(msg))})
    await message.answer(text="Введите стоимость продажи объекта:", reply_markup=keyboards.back_keyboard, parse_mode="HTML")
    await state.set_state(Heritage.sell)


@router.message(Heritage.sell)
async def heritage_sell(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"sold": utils.check_number(str(msg))})
    data = await state.get_data()
    await state.clear()

    date, sell, cadastral = data["date"].split("."), data["sold"], data["cadastral"]
    date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
    different_date = datetime.datetime.now() - date

    sell = max(sell, cadastral * 0.7)

    if int(str(different_date).split()[0]) // 365 < 3:
        await message.answer(text=texts.heritage_false(sell), parse_mode="HTML")
        return await message.answer(text=texts.heritage_text, reply_markup=keyboards.back_keyboard, parse_mode="HTML")
    await message.answer(text=texts.buysell_true, reply_markup=keyboards.back_keyboard, parse_mode="HTML")


class Share(StatesGroup):
    ratio = State()
    area_sell = State()
    sell_value = State()
    area_buy = State()
    buy_value = State()


@router.callback_query(F.data == "share_calculator")
async def share_calculator(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()

    user_id = int(callback.from_user.id)
    if crud_users.get_user_status(user_id) == 0:
        "не подписан, прописываем подписку"
        return await callback.message.answer(
            text=texts.payment_message,
            reply_markup=keyboards.get_trial, parse_mode="HTML"
        )

    await callback.message.answer(text="Введите размер доли ребенка в продаваемой квартире", parse_mode="HTML")
    await state.set_state(Share.ratio)


@router.message(Share.ratio)
async def share_ratio(message: Message, state: FSMContext):
    msg = message.text
    pat = r"\d\/\d"
    if not re.findall(pat, msg):
        return message.answer(
            text="Вы ввели не долю. Введите долю. Например: 6/7, 8/11",
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"ratio": str(msg)})
    await message.answer(text="Площадь продаваемой квартиры (В кв.м.)", parse_mode="HTML")
    await state.set_state(Share.area_sell)


@router.message(Share.area_sell)
async def share_area_sell(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"area_sell": utils.check_number(str(msg))})
    await message.answer(text="Введите кадастровую стоимость продаваемой квартиры", parse_mode="HTML")
    await state.set_state(Share.sell_value)


@router.message(Share.sell_value)
async def share_sell_value(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"sell_value": utils.check_number(str(msg))})
    await message.answer(text="Введите площадь приобретаемой квартиры (В кв.м.)", parse_mode="HTML")
    await state.set_state(Share.area_buy)


@router.message(Share.area_buy)
async def share_area_buy(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )

    await state.update_data({"area_buy": utils.check_number(str(msg))})
    await message.answer(text="Введите кадастровую стоимость приобретаемой квартиры", parse_mode="HTML")
    await state.set_state(Share.buy_value)


@router.message(Share.buy_value)
async def share_buy_value(message: Message, state: FSMContext):
    msg = message.text
    if utils.check_number(str(msg)) == "error":
        return await message.answer(
            text=texts.error_format_of_number,
            reply_markup=keyboards.back_keyboard, parse_mode="HTML"
        )
    await state.update_data({"buy_value": utils.check_number(str(msg))})
    data = await state.get_data()
    await state.clear()

    ratio = data["ratio"]
    ratio = float(eval(ratio))
    area_sell = data["area_sell"]
    sell_value = data["sell_value"]
    area_buy = data["area_buy"]
    buy_value = data["buy_value"]
    try:
        real_sell_value = round(sell_value / area_sell, 2)
        real_buy_value = round(buy_value / area_buy, 2)
        real_sell_ratio = area_sell * ratio
        real_ratio = real_sell_value * real_sell_ratio
        needed_ratio = real_ratio / real_buy_value
    except:
        return await message.answer(text="Начните заново и введите корректные данные",
                                    reply_markup=keyboards.back_keyboard, parse_mode="HTML")
    if needed_ratio > 6:
        needed_ratio = max(needed_ratio, real_sell_ratio)
    else:
        needed_ratio = 6.000
    part = needed_ratio / area_buy
    # part = "".join(list(map(str, utils.findFraction(str(part)))))
    text = texts.share_text(real_sell_value, real_buy_value, real_sell_ratio, real_ratio, needed_ratio, part)
    await message.answer(text=text, reply_markup=keyboards.back_keyboard, parse_mode="HTML")
