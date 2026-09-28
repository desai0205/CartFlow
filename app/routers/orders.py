from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


def _serialize_order(order: Order) -> OrderResponse:
    items = []
    for item in order.items:
        item_resp = OrderItemResponse.model_validate(item)
        item_resp.subtotal = Decimal(item.unit_price) * item.quantity
        items.append(item_resp)

    response = OrderResponse.model_validate(order)
    response.items = items
    return response


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_items = list(
        db.scalars(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.user_id == current_user.id)
        )
        .unique()
        .all()
    )
    if not cart_items:
        raise BadRequestError("Cart is empty")

    total_amount = Decimal("0.00")
    order_items_data: list[dict] = []

    for cart_item in cart_items:
        product = cart_item.product
        if not product.is_active:
            raise BadRequestError(f"Product '{product.name}' is no longer available")
        if product.stock < cart_item.quantity:
            raise BadRequestError(
                f"Insufficient stock for '{product.name}'. Available: {product.stock}"
            )

        unit_price = Decimal(product.price)
        total_amount += unit_price * cart_item.quantity
        order_items_data.append(
            {
                "product": product,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
            }
        )

    order = Order(
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        shipping_address=payload.shipping_address,
    )
    db.add(order)
    db.flush()

    for data in order_items_data:
        product: Product = data["product"]
        product.stock -= data["quantity"]
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=data["quantity"],
                unit_price=data["unit_price"],
            )
        )

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()

    order = db.scalar(
        select(Order)
        .options(joinedload(Order.items))
        .where(Order.id == order.id)
    )
    return _serialize_order(order)


@router.get("", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Order).options(joinedload(Order.items)).order_by(Order.id.desc())
    if current_user.role != UserRole.ADMIN:
        query = query.where(Order.user_id == current_user.id)

    orders = db.scalars(query).unique().all()
    return [_serialize_order(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.scalar(
        select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
    )
    if not order:
        raise NotFoundError("Order not found")
    if current_user.role != UserRole.ADMIN and order.user_id != current_user.id:
        raise ForbiddenError("Not allowed to view this order")
    return _serialize_order(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    order = db.scalar(
        select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
    )
    if not order:
        raise NotFoundError("Order not found")

    if order.status == OrderStatus.CANCELLED:
        raise BadRequestError("Cancelled orders cannot be updated")

    # Restore stock when cancelling a non-cancelled order
    if payload.status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.get(Product, item.product_id)
            if product:
                product.stock += item.quantity

    order.status = payload.status
    db.commit()
    db.refresh(order)
    order = db.scalar(
        select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
    )
    return _serialize_order(order)
