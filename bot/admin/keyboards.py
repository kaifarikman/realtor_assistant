from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_menu_buttons = [
    [
        InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")
    ]
]

back_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=back_menu_buttons)

admin_back_menu_buttons = [
    [
        InlineKeyboardButton(text="Вернуться в админ меню", callback_data="admin")
    ],
    [
        InlineKeyboardButton(text="Вернуться в главное меню", callback_data="start")
    ]
]

admin_back_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=admin_back_menu_buttons)

admin_buttons = [
    [
        InlineKeyboardButton(text="Просмотреть список пользоватлей бота", callback_data="watch_users")
    ],
    [
        InlineKeyboardButton(text="Пользователи с подпиской", callback_data="watch_white_users")
    ],
    [
        InlineKeyboardButton(text="Выдать подписку", callback_data="issue_subscription")
    ]
]

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=admin_buttons)
