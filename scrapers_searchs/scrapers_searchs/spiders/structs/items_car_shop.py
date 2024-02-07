from typing import List

from pydantic import BaseModel


class OrderItem(BaseModel):
    quantity: int
    seller: str
    id: str
    index: int


class BuildItems(BaseModel):
    orderItems: List[OrderItem]
