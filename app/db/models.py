from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    BigInteger, Boolean, Date, DateTime, String, text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, server_default='UTC')
    weekly_subscription: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    last_sent: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('now()'),
        onupdate=datetime.utcnow
    )
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    language_code: Mapped[str] = mapped_column(String(50), nullable=False)
