from datetime import datetime, date
from aiogram import types
from sqlalchemy import select, update

from app.core.database import get_session
from app.db.models import User


async def add_user(
        message: types.Message,
        birth_date: date
) -> User:
    """Добавляет нового пользователя."""
    telegram_user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""
    timezone = message.from_user.language_code or "UTC"
    language_code = message.from_user.language_code or ""
    is_premium = message.from_user.is_premium or False
    is_bot = message.from_user.is_bot

    async with get_session() as session:
        user = User(
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            birth_date=birth_date,
            timezone=timezone,
            is_premium=is_premium,
            is_bot=is_bot,
            language_code=language_code,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)


async def get_user_by_telegram_id(telegram_user_id: int) -> User | None:
    """Возвращает пользователя по Telegram ID, если он существует."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
        return result.scalar_one_or_none()


async def set_weekly_subscription(telegram_user_id: int, value: bool) -> None:
    """Изменяет значение флага weekly_subscription для пользователя."""
    async with get_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_user_id == telegram_user_id)
            .values(weekly_subscription=value, updated_at=datetime.utcnow())
        )
        await session.commit()


async def update_birth_date(telegram_user_id: int, birth_date: date) -> None:
    """Изменяет дату рождения пользователя."""
    async with get_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_user_id == telegram_user_id)
            .values(birth_date=birth_date, updated_at=datetime.utcnow())
        )
        await session.commit()
