from pydantic import BaseModel, EmailStr, Field


class ItemBase(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str | None = Field(max_length=500)
    user_id: int


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str | None = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    address: str | None = Field(max_length=500)


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    items: list[Item] = []

    class Config:
        from_attributes = True
