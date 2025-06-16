import asyncio

from app.core.database import init_db, close_db
from app.telegram.bot import dp, bot


async def main() -> None:
    await init_db()
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
