from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, default=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartProductInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    stock: int


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime
    product: CartProductInfo
    subtotal: Decimal = Decimal("0.00")


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    total_amount: Decimal
