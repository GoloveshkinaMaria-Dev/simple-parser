from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ParseJobORM(Base):
    __tablename__ = "parse_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    area: Mapped[int | None] = mapped_column()
    status: Mapped[str] = mapped_column()
    items_count: Mapped[int] = mapped_column(default=0)
    per_page: Mapped[int] = mapped_column(default=20)
    max_pages: Mapped[int] = mapped_column(default=5)
    error: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
