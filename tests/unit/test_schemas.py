import unittest

from pydantic import ValidationError

from src import schemas


class TestSchemas(unittest.TestCase):
    def testUserBase(self):
        data = {
            "name": "John Doe",
            "email": "test@mail.com",
            "address": "some address",
        }

        user = schemas.UserBase(**data)

        self.assertDictEqual(user.model_dump(), data)

    def testUserBase_BadEmail(self):
        data = {
            "name": "John Doe",
            "email": "test",
            "address": "some address",
        }

        with self.assertRaises(ValidationError):
            schemas.UserBase(**data)

    def testUser(self):
        data = {
            "name": "John Doe",
            "email": "test@mail.com",
            "address": "some address",
            "id": 1,
            "items": [
                {
                    "title": "Book",
                    "description": "foobar",
                    "user_id": 1,
                    "id": 1,
                },
            ],
        }

        user = schemas.User(**data)

        self.assertDictEqual(user.model_dump(), data)

    def testItemBase(self):
        data = {
            "title": "Book",
            "description": "foobar",
            "user_id": 1,
        }
        item = schemas.ItemBase(**data)

        self.assertDictEqual(item.model_dump(), data)

    def testItemBase_BadTitle(self):
        data = {
            "title": "",
            "description": "foobar",
            "user_id": 1,
        }

        with self.assertRaises(ValidationError):
            schemas.ItemBase(**data)

    def testItem(self):
        data = {
            "title": "Book",
            "description": "foobar",
            "user_id": 1,
            "id": 1,
        }
        item = schemas.Item(**data)

        self.assertDictEqual(item.model_dump(), data)
