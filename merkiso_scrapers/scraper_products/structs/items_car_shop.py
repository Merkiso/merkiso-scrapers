from pydantic import BaseModel
from typing import List


class OrderItem(BaseModel):
    quantity: int
    seller: str
    id: str
    index: int


class BuildItems(BaseModel):
    orderItems: List[OrderItem]
