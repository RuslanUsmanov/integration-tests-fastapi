import os
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, insert
from sqlalchemy.orm import sessionmaker

from src import models
from src.database import get_db
from src.main import app

DB_URL = "sqlite:///test.db"

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """
    Заменяет зависимость БД на тестовую БД
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        models.Base.metadata.create_all(bind=engine)

        # Переписываем зависимость
        app.dependency_overrides[get_db] = override_get_db

        # Создаем тестовый клиент
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        # После всех тестов удаляем файл
        os.remove("./test.db")

    def tearDown(self) -> None:
        # После каждого теста очищаем БД
        db = next(override_get_db())
        db.execute(delete(models.User))
        db.execute(delete(models.Item))
        db.commit()

    def testCreateUser(self):
        # Выполняем запрос к эндпоинту для создание пользователя
        response = self.client.post(
            "/users/",
            json={
                "name": "John Doe",
                "email": "test@mail.com",
                "address": "some addr",
            },
        )

        self.assertEqual(201, response.status_code)

        data = response.json()

        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "test@mail.com")
        self.assertEqual(data["address"], "some addr")

    def testCreateUser_BadEmail(self):
        response = self.client.post(
            "/users/",
            json={
                "name": "John Doe",
                "email": "test",
                "address": "some addr",
            },
        )

        self.assertEqual(422, response.status_code)

        data = response.json()
        type = data["detail"][0]["type"]
        self.assertEqual(type, "value_error")

    def testGetUsers(self):
        db = next(override_get_db())
        db_users = db.scalars(
            insert(models.User).returning(models.User),
            [
                {
                    "name": "John",
                    "email": "john@mail.com",
                    "address": "addr1 john",
                },
                {
                    "name": "Bob",
                    "email": "bob@mail.com",
                    "address": "addr2 bob",
                },
            ],
        ).all()

        db.commit()

        response = self.client.get("/users/")

        self.assertEqual(200, response.status_code)

        data = response.json()

        self.assertEqual(2, len(data))
        self.assertEqual(db_users[0].email, data[0]["email"])
        self.assertEqual(db_users[1].email, data[1]["email"])

    def testDeleteUser(self):
        db = next(override_get_db())
        db_user = models.User(
            name="John", email="test@mail.com", address="address"
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()

        response = self.client.delete(f"/users/{db_user.id}")

        self.assertEqual(204, response.status_code)

        user = db.get(models.User, db_user.id)

        self.assertIsNone(user)
