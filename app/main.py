import asyncio
import pydevd_pycharm


from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.bots.telegram.handlers import router


bot = Bot(token=settings.TOKEN)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    pydevd_pycharm.settrace('host.docker.internal', port=12345, stdoutToServer=True, stderrToServer=True, suspend=False)
    print("Бот запущен")
    asyncio.run(main())

