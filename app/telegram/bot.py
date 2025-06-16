from aiogram import Bot, Dispatcher

from app.core.config import settings
from .handlers import start, birthdate

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(birthdate.router)
