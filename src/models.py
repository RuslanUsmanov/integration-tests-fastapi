from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, MappedAsDataclass):
    """
    Базовый класс для моделей. Подключено отображение в dataclass'ы
    """

    pass


class BaseModel(Base):
    """
    Абстрактная модель, в которой описан первичный ключ для всех наследуемых
    от него моделей
    """

    __abstract__ = True
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        init=False,
        nullable=False,
    )


class User(BaseModel):
    """
    Модель пользователей
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    address: Mapped[str] = mapped_column(String(500), nullable=True)

    items: Mapped[list["Item"]] = relationship("Item", init=False)


class Item(BaseModel):
    """
    Модель элементов
    """

    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    # owner: Mapped["User"] = relationship(
    #     "User", back_populates="items", init=False
    # )
