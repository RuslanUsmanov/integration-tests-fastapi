import unittest

from sqlalchemy import create_engine, delete, insert, select
from sqlalchemy.orm import Session

from src import models, schemas
from src.internal.crud import item as crud

DB_URL = "sqlite:///:memory:"  # БД в памяти


class TestCrudItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Устанавливает соединение с БД и создает все таблицы
        """
        cls.engine = create_engine(DB_URL)
        models.Base.metadata.create_all(bind=cls.engine)
        cls.db = Session(bind=cls.engine)
        # Перед всеми тестами создаем пользователя
        cls.db.add(
            models.User(
                name="John Doe", email="test@mail.com", address="some addr"
            )
        )
        cls.db.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Закрывает соединение после всех тестов
        """
        cls.db.execute(delete(models.User))
        cls.db.commit()
        cls.db.close()

    def tearDown(self):
        """
        Делает коммит после каждого теста
        """
        self.db.commit()

    def test_create_item(self):
        """
        Тест создания элемента
        """
        # Заполняем модель
        item = schemas.ItemCreate(
            title="book", description="foo bar 123", user_id=1
        )
        # Вызываем функцию создания пользователя
        db_item = crud.create_item(item=item, db=self.db)

        # Проверяем, что вернулся правильный тип
        self.assertIsInstance(db_item, models.Item)
        self.assertIsInstance(db_item.id, int)
        # Выполняем запрос к БД, ищем добавленного пользователя по ID
        db_item = self.db.get(models.Item, db_item.id)
        # Проверяем поля
        self.assertEqual(item.title, db_item.title)
        self.assertEqual(item.description, db_item.description)
        self.assertEqual(item.user_id, db_item.user_id)

        self.db.delete(db_item)

    def test_get_items(self):
        items = self.db.scalars(
            insert(models.Item).returning(models.Item),
            [
                {
                    "title": "Book",
                    "description": "foobar",
                    "user_id": "1",
                },
                {
                    "title": "Pen",
                    "description": "",
                    "user_id": "1",
                },
            ],
        ).all()

        self.db.commit()

        db_items = crud.get_items(db=self.db).all()

        # Проверяем длины списоков
        self.assertEqual(len(db_items), len(items))
        # Проверяем равенство списоков
        self.assertListEqual(db_items, items)

        self.db.execute(delete(models.Item))

    def test_get_item_by_id(self):
        db_item = models.Item(
            title="Book",
            description="foobar",
            user_id=1,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        item = crud.get_item_by_id(id=db_item.id, db=self.db)

        self.assertIsInstance(item, models.Item)
        self.assertEqual(item.title, db_item.title)
        self.assertEqual(item.description, db_item.description)
        self.assertEqual(item.user_id, db_item.user_id)

        self.db.delete(db_item)

    def test_update_item(self):
        """
        Тест обновления пользователя
        """
        db_item = models.Item(
            title="Book",
            description="foobar",
            user_id=1,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        item_new = schemas.ItemCreate(
            title="Sketchpad",
            description="new descr",
            user_id=1,
        )

        db_item = crud.update_item(db_item=db_item, item=item_new, db=self.db)

        self.assertIsInstance(db_item, models.Item)
        self.assertEqual(item_new.title, db_item.title)
        self.assertEqual(item_new.description, db_item.description)
        self.assertEqual(item_new.user_id, db_item.user_id)

        self.db.delete(db_item)

    def test_delete_item(self):
        """
        Тест удаления пользователя
        """
        db_item = crud.create_item(
            item=schemas.ItemCreate(
                title="Book",
                description="foobar",
                user_id=1,
            ),
            db=self.db,
        )

        crud.delete_item(db_item=db_item, db=self.db)

        db_item = self.db.scalar(select(models.Item))

        self.assertNotIsInstance(db_item, models.Item)
        self.assertIsNone(db_item)
