from aiogram import Router, types
from aiogram.filters import Command
import datetime

from app.services.life_calendar import create_life_calendar_image
from app.services.user_service import (
    add_or_update_user_data,
    get_user_by_telegram_id,
    set_weekly_subscription,
    update_birth_date,
)
from .keyboards import start_keyboard, main_keyboard

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user is None:
        await message.answer(
            "Привет! Нажми кнопку \"Старт\" и пришли дату рождения в формате ДД.ММ.ГГГГ",
            reply_markup=start_keyboard(),
        )
    else:
        await message.answer(
            "Выберите действие:",
            reply_markup=main_keyboard(user.weekly_subscription),
        )


@router.message(lambda m: m.text and m.text.lower() == "старт")
async def start_button(message: types.Message):
    await message.answer("Отправь дату рождения в формате ДД.ММ.ГГГГ")


@router.message(lambda m: m.text and m.text.lower() == "изменить дату рождения")
async def change_birthdate(message: types.Message):
    await message.answer("Пришли новую дату рождения в формате ДД.ММ.ГГГГ")


@router.message(lambda m: m.text and m.text.lower() == "отправить календарь")
async def send_calendar(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or not user.birth_date:
        await message.answer("Сначала отправьте дату рождения командой Старт")
        return
    await _send_calendar_for_user(message, user.birth_date, user.weekly_subscription)


@router.message(lambda m: m.text and m.text.lower() == "отключить рассылку")
async def disable_subscription(message: types.Message):
    await set_weekly_subscription(message.from_user.id, False)
    await message.answer(
        "Рассылка отключена",
        reply_markup=main_keyboard(False),
    )


@router.message(lambda m: m.text and m.text.lower() == "подключить рассылку")
async def enable_subscription(message: types.Message):
    await set_weekly_subscription(message.from_user.id, True)
    await message.answer(
        "Рассылка подключена",
        reply_markup=main_keyboard(True),
    )


@router.message()
async def process_birthdate(message: types.Message):
    try:
        birth_date = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используй формат ДД.ММ.ГГГГ.")
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        await update_birth_date(message.from_user.id, birth_date)
    else:
        await add_or_update_user_data(message, birth_date)
    user = await get_user_by_telegram_id(message.from_user.id)
    subscription = user.weekly_subscription if user else False
    await _send_calendar_for_user(message, birth_date, subscription)


async def _send_calendar_for_user(message: types.Message, birth_date: datetime.date, subscription: bool) -> None:
    today = datetime.date.today()
    try:
        hundred_birthday = birth_date.replace(year=birth_date.year + 100)
    except ValueError:
        hundred_birthday = birth_date.replace(year=birth_date.year + 100, day=28)

    if today >= hundred_birthday:
        await message.answer("Ты уже прожил(а) более 100 лет!")
        return

    total_days = (hundred_birthday - birth_date).days
    total_weeks = total_days // 7

    passed_days = (today - birth_date).days
    passed_weeks = passed_days // 7

    remaining_weeks = total_weeks - passed_weeks

    text_response = (
        f"Всего недель в 100 лет: {total_weeks}\n"
        f"Прожито недель: {passed_weeks}\n"
        f"Осталось недель: {remaining_weeks}"
    )

    max_grid_weeks = 52 * 100
    passed_weeks_clamped = min(passed_weeks, max_grid_weeks)

    image = create_life_calendar_image(passed_weeks_clamped)
    import io
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    img_bytes = img_buffer.getvalue()

    await message.answer_photo(
        photo=types.BufferedInputFile(img_bytes, filename="life_calendar.png"),
        caption=text_response,
        reply_markup=main_keyboard(subscription),
    )
