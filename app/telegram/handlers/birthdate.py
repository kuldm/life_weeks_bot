import datetime
import io
from aiogram import Router, types

from app.services.life_calendar import create_life_calendar_image
from app.services.user_service import add_or_update_user_data

router = Router()

@router.message()
async def process_birthdate(message: types.Message):
    try:
        birth_date = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используй формат ДД.ММ.ГГГГ.")
        return

    today = datetime.date.today()
    try:
        hundred_birthday = birth_date.replace(year=birth_date.year + 100)
    except ValueError:
        hundred_birthday = birth_date.replace(year=birth_date.year + 100, day=28)

    if today >= hundred_birthday:
        await message.answer("Ты уже прожил(а) более 100 лет!")
        return

    await add_or_update_user_data(message, birth_date)
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
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_bytes = img_buffer.getvalue()
    await message.answer_photo(
        photo=types.BufferedInputFile(img_bytes, filename="life_calendar.png"),
        caption=text_response
    )
