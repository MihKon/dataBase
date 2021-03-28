from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    id: int
    field1: str
    field2: str


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    class Config:
        orm_mode = True
