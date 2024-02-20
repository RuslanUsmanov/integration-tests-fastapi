import unittest

from sqlalchemy import create_engine, delete, insert, select
from sqlalchemy.orm import Session

from src import models, schemas
from src.internal.crud import user as crud

DB_URL = "sqlite:///:memory:"  # БД в памяти


class TestCrudUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Устанавливает соединение с БД и создает все таблицы
        """
        cls.engine = create_engine(DB_URL)
        models.Base.metadata.create_all(bind=cls.engine)
        cls.db = Session(bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Закрывает соединение после всех тестов
        """
        cls.db.close()

    def tearDown(self):
        """
        Делает коммит после каждого теста
        """
        self.db.commit()

    def test_create_user(self):
        """
        Тест создания пользователя
        """
        # Заполняем модель
        user = schemas.UserCreate(
            name="Jack Black", email="test@mail.com", address="some address"
        )
        # Вызываем функцию создания пользователя
        db_user = crud.create_user(user=user, db=self.db)

        # Проверяем, что вернулся правильный тип
        self.assertIsInstance(db_user, models.User)
        self.assertIsInstance(db_user.id, int)
        # Выполняем запрос к БД, ищем добавленного пользователя по ID
        db_user = self.db.get(models.User, db_user.id)
        # Проверяем поля
        self.assertEqual(user.name, db_user.name)
        self.assertEqual(user.email, db_user.email)
        self.assertEqual(user.address, db_user.address)

        self.db.delete(db_user)

    def test_get_users(self):
        users = self.db.scalars(
            insert(models.User).returning(models.User),
            [
                {
                    "name": "Jack Black",
                    "email": "test@mail.com",
                    "address": "some address",
                },
                {
                    "name": "John Doe",
                    "email": "john@doe.com",
                    "address": "new address",
                },
            ],
        ).all()

        self.db.commit()

        db_users = crud.get_users(db=self.db).all()

        # Проверяем длины списоков
        self.assertEqual(len(db_users), len(users))
        # Проверяем равенство списоков
        self.assertListEqual(db_users, users)

        self.db.execute(delete(models.User))

    def test_get_user_by_id(self):
        db_user = models.User(
            name="Jack Black",
            email="test@mail.com",
            address="some address",
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        user = crud.get_user_by_id(id=db_user.id, db=self.db)

        self.assertIsInstance(user, models.User)
        self.assertEqual(user.name, db_user.name)
        self.assertEqual(user.email, db_user.email)
        self.assertEqual(user.address, db_user.address)

        self.db.delete(db_user)

    def test_get_user_by_email(self):
        db_user = models.User(
            name="Jack Black",
            email="test@mail.com",
            address="some address",
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        user = crud.get_user_by_email(email=db_user.email, db=self.db)

        self.assertIsInstance(user, models.User)
        self.assertEqual(user.name, db_user.name)
        self.assertEqual(user.email, db_user.email)
        self.assertEqual(user.address, db_user.address)

        self.db.delete(db_user)

    def test_update_user(self):
        """
        Тест обновления пользователя
        """
        db_user = models.User(
            name="Jack Black",
            email="test@mail.com",
            address="some address",
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        user_new = schemas.UserCreate(
            name="John Doe", email="john@doe.com", address="address new"
        )

        db_user = crud.update_user(db_user=db_user, user=user_new, db=self.db)

        self.assertIsInstance(db_user, models.User)
        self.assertEqual(user_new.name, db_user.name)
        self.assertEqual(user_new.email, db_user.email)
        self.assertEqual(user_new.address, db_user.address)

        self.db.delete(db_user)

    def test_delete_user(self):
        """
        Тест удаления пользователя
        """
        db_user = crud.create_user(
            user=schemas.UserCreate(
                name="Jack Black",
                email="test@mail.com",
                address="some address",
            ),
            db=self.db,
        )

        crud.delete_user(db_user=db_user, db=self.db)

        db_user = self.db.scalar(select(models.User))

        self.assertNotIsInstance(db_user, models.User)
        self.assertIsNone(db_user)
