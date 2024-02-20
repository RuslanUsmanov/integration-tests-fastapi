from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base

# Адрес подключения к БД
SQLALCHEMY_DATABASE_URL = "sqlite:///local.db"

# Настраиваем engine подключения
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Настраиваем свой класс для сессии БД
SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_db():
    """
    Генератор сессий БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """
    Создает таблицы в БД (также создается файл БД, если используется sqlite).
    Таблицы создаются на основе моделей из src/models.py.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_database()
