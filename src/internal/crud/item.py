from sqlalchemy import select
from sqlalchemy.orm import Session

from src import models, schemas


def get_items(db: Session) -> list[models.Item]:
    """
    Возвращает список элементов из БД.
    """
    return db.scalars(select(models.Item))


def get_item_by_id(id: int, db: Session) -> models.Item:
    """
    Возвращает элемент по указанному id.
    """
    return db.get(models.Item, id)


def create_item(item: schemas.ItemCreate, db: Session) -> models.Item:
    """
    Создает новый элемент на основе полей схемы item.
    Возвращает созданный экземпляр модели Item.
    """
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(
    db_item: models.Item, item: schemas.ItemCreate, db: Session
) -> models.Item:
    """
    Обновляет экземпляр db_item значениями из схемы item.
    Возвращает обновленный экземпляр модели Item.
    """
    update_data = item.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def delete_item(db_item: models.Item, db: Session) -> None:
    """
    Удаяет элемент db_item.
    Возвращает None.
    """
    db.delete(db_item)
    db.commit()
    return None
