from sqlalchemy import select
from sqlalchemy.orm import Session

from src import models, schemas


def get_users(db: Session) -> list[models.User]:
    """
    Возвращает и БД список пользователей
    """
    return db.scalars(select(models.User))


def get_user_by_id(id: int, db: Session) -> models.User:
    """
    Возвращает пользователя по указанному id
    """
    return db.get(models.User, id)


def get_user_by_email(email: str, db: Session) -> models.User:
    """
    Возвращает пользователя по указанному email
    """
    return db.scalar(select(models.User).where(models.User.email == email))


def create_user(user: schemas.UserCreate, db: Session) -> models.User:
    """
    Создает нового пользователя в БД из полей схемы user.
    Возвращает созданный экземпляр модели User.
    """
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db_user: models.User, user: schemas.UserCreate, db: Session
) -> models.User:
    """
    Обновляет поля пользователя db_user значениями из схемы user.
    Возвращает обновленный экземпляр модели User.
    """
    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(db_user: models.User, db: Session) -> None:
    """
    Удаляет из БД указаного пользователя.
    Возвращает None.
    """
    db.delete(db_user)
    db.commit()
    return None
