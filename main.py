import asyncio
import datetime

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command

from settings import settings
from src.services.generate_image import create_life_calendar_image
from src.services.update_info import add_or_update_user_data

bot = Bot(token=settings.TOKEN)
router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Отправь мне дату своего рождения в формате ДД.ММ.ГГГГ")


@router.message()
async def process_birthdate(message: types.Message):
    # Парсинг даты рождения
    try:
        birth_date = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используй формат ДД.ММ.ГГГГ.")
        return

    today = datetime.date.today()

    # Определяем дату, когда исполнится 100 лет
    try:
        hundred_birthday = birth_date.replace(year=birth_date.year + 100)
    except ValueError:
        # Если дата рождения 29 февраля, корректируем до 28 февраля
        hundred_birthday = birth_date.replace(year=birth_date.year + 100, day=28)

    if today >= hundred_birthday:
        await message.answer("Ты уже прожил(а) более 100 лет!")
        return

    await add_or_update_user_data(message, birth_date)
    # Подсчёт общего количества недель до 100 лет (вычисление на базе разницы в днях)
    total_days = (hundred_birthday - birth_date).days
    total_weeks = total_days // 7

    # Подсчёт прожитых недель
    passed_days = (today - birth_date).days
    passed_weeks = passed_days // 7

    remaining_weeks = total_weeks - passed_weeks

    # Формируем текстовый результат для подписи картинки
    text_response = (
        f"Всего недель в 100 лет: {total_weeks}\n"
        f"Прожито недель: {passed_weeks}\n"
        f"Осталось недель: {remaining_weeks}"
    )

    # Ограничиваем количество недель для визуальной сетки (5200 недель)
    max_grid_weeks = 52 * 100  # 5200 недель
    passed_weeks_clamped = min(passed_weeks, max_grid_weeks)

    # Генерируем изображение календаря жизни
    image = create_life_calendar_image(passed_weeks_clamped)
    import io  # если ранее не импортировали
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # Получаем байтовые данные для отправки
    img_bytes = img_buffer.getvalue()

    # Отправляем изображение с подписью в одном сообщении
    await message.answer_photo(
        photo=types.BufferedInputFile(img_bytes, filename="life_calendar.png"),
        caption=text_response
    )


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    print("Бот запущен")
    asyncio.run(main())
