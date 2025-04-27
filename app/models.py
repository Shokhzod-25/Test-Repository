from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Items(Base):
    __tablename__ = 'items'

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
