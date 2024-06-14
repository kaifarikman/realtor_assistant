from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_buttons = [
    [
        InlineKeyboardButton(text="Выйти в главное меню", callback_data="start")
    ]
]

back_keyboard = InlineKeyboardMarkup(inline_keyboard=back_buttons)

start_buttons = [
    [
        InlineKeyboardButton(text="📕Расчет платежа по ипотеке", callback_data="mortgage_payment_calculation")
    ],
    [
        InlineKeyboardButton(text="📗Калькулятор завышения", callback_data="overstatement_calculator")
    ],
    [
        InlineKeyboardButton(text="📘Налоговый калькулятор", callback_data="tax_calculator")
    ],
    [
        InlineKeyboardButton(text="📙Калькулятор долей", callback_data="share_calculator")
    ]
]

start_keyboard = InlineKeyboardMarkup(inline_keyboard=start_buttons)

tax_buttons = [
    [
        InlineKeyboardButton(text="Купля-продажа/Мена", callback_data="buysell_calculator"),
        InlineKeyboardButton(text="Дарение", callback_data="gift_calculator")
    ],
    [
        InlineKeyboardButton(text="Долевое участие / Уступка права требования", callback_data="assignment_calculator")
    ],
    [
        InlineKeyboardButton(text="Приватизация", callback_data="privatization_calculator"),
        InlineKeyboardButton(text="Наследство", callback_data="heritage_calculator")
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data="start")
    ]
]

tax_keyboard = InlineKeyboardMarkup(inline_keyboard=tax_buttons)

buysell_buttons = [
    [
        InlineKeyboardButton(text="Да", callback_data="buysell_yes"),
        InlineKeyboardButton(text="Нет", callback_data="buysell_no")
    ]
]

buysell_keyboard = InlineKeyboardMarkup(inline_keyboard=buysell_buttons)

assignment_buttons = [
    [
        InlineKeyboardButton(text="Да", callback_data="assignment_yes"),
        InlineKeyboardButton(text="Нет", callback_data="assignment_no")
    ]
]

assignment_keyboard = InlineKeyboardMarkup(inline_keyboard=assignment_buttons)

trial_buttons = [[InlineKeyboardButton(text="Пробная подписка", callback_data="get_trial")]]
get_trial = InlineKeyboardMarkup(inline_keyboard=trial_buttons)
