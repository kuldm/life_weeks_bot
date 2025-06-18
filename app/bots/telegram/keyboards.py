from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с единственной кнопкой "Старт"."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_keyboard(subscription_enabled: bool) -> ReplyKeyboardMarkup:
    """Основная клавиатура в зависимости от статуса подписки."""
    buttons = [
        [KeyboardButton(text="Отправить календарь")],
        [KeyboardButton(text="Изменить дату рождения")],
    ]
    if subscription_enabled:
        buttons.append([KeyboardButton(text="Отключить рассылку")])
    else:
        buttons.append([KeyboardButton(text="Подключить рассылку")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)