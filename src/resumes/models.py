from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ResumeORM(Base):
    __tablename__ = "resume"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("parse_job.id", ondelete="CASCADE"),
        index=True,
    )
    external_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    area_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    area_name: Mapped[str] = mapped_column(String(255), default="")
    salary_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    url: Mapped[str] = mapped_column(String(1024))
    work_format: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    skills: Mapped[list["ResumeSkillORM"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    __table_args__ = (Index("ix_resume_area_salary", "area_id", "salary_amount"),)


class ResumeSkillORM(Base):
    __tablename__ = "resume_skill"

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resume.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)

    resume: Mapped["ResumeORM"] = relationship(back_populates="skills")
