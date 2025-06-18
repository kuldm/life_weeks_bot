from datetime import datetime, date
from aiogram import types
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.db.models import User

async def add_or_update_user_data(
    message: types.Message,
    birth_date: date
) -> User:
    """
    Добавляет нового пользователя или обновляет существующего на основе данных из message и birth_date.
    """
    telegram_user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""
    timezone = message.from_user.language_code or "UTC"
    language_code = message.from_user.language_code or ""
    is_premium = message.from_user.is_premium
    is_bot = message.from_user.is_bot

    async with get_session() as session:
        # Попытка найти существующего пользователя
        result = await session.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Обновляем найденного пользователя
            await session.execute(
                update(User)
                .where(User.telegram_user_id == telegram_user_id)
                .values(
                    chat_id=chat_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    birth_date=birth_date,
                    timezone=timezone,
                    language_code=language_code,
                    is_premium=is_premium,
                    is_bot=is_bot,
                    updated_at=datetime.utcnow(),
                )
            )
            await session.commit()
            await session.refresh(user)
        else:
            # Создаём нового пользователя
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

        return user

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


async def update_user_birthday(telegram_user_id: int, value: bool) -> None:
    """Изменяет значение дня рождения для пользователя."""
    async with get_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_user_id == telegram_user_id)
            .values(birth_date=value, updated_at=datetime.utcnow())
        )
        await session.commit()