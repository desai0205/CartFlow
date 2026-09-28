from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"])


def _build_cart_response(items: list[CartItem]) -> CartResponse:
    response_items: list[CartItemResponse] = []
    total_amount = Decimal("0.00")
    total_items = 0

    for item in items:
        subtotal = Decimal(item.product.price) * item.quantity
        cart_item = CartItemResponse.model_validate(item)
        cart_item.subtotal = subtotal
        response_items.append(cart_item)
        total_amount += subtotal
        total_items += item.quantity

    return CartResponse(
        items=response_items,
        total_items=total_items,
        total_amount=total_amount,
    )


def _get_user_cart_items(db: Session, user_id: int) -> list[CartItem]:
    return list(
        db.scalars(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        )
        .unique()
        .all()
    )


@router.get("", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = _get_user_cart_items(db, current_user.id)
    return _build_cart_response(items)


@router.post("/items", response_model=CartResponse, status_code=201)
def add_to_cart(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.get(Product, payload.product_id)
    if not product or not product.is_active:
        raise NotFoundError("Product not found")
    if product.stock < payload.quantity:
        raise BadRequestError(f"Insufficient stock. Available: {product.stock}")

    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == payload.product_id,
        )
    )
    if cart_item:
        new_qty = cart_item.quantity + payload.quantity
        if product.stock < new_qty:
            raise BadRequestError(f"Insufficient stock. Available: {product.stock}")
        cart_item.quantity = new_qty
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(cart_item)

    db.commit()
    return _build_cart_response(_get_user_cart_items(db, current_user.id))


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_item = db.scalar(
        select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.id == item_id, CartItem.user_id == current_user.id)
    )
    if not cart_item:
        raise NotFoundError("Cart item not found")
    if cart_item.product.stock < payload.quantity:
        raise BadRequestError(f"Insufficient stock. Available: {cart_item.product.stock}")

    cart_item.quantity = payload.quantity
    db.commit()
    return _build_cart_response(_get_user_cart_items(db, current_user.id))


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_item = db.scalar(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == current_user.id)
    )
    if not cart_item:
        raise NotFoundError("Cart item not found")

    db.delete(cart_item)
    db.commit()
    return _build_cart_response(_get_user_cart_items(db, current_user.id))


@router.delete("", response_model=CartResponse)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.scalars(select(CartItem).where(CartItem.user_id == current_user.id)).all()
    for item in items:
        db.delete(item)
    db.commit()
    return CartResponse(items=[], total_items=0, total_amount=Decimal("0.00"))
