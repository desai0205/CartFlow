from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    shipping_address: str = Field(min_length=5, max_length=500)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal = Decimal("0.00")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []
