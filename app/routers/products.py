from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, StockUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    query = select(Product).options(joinedload(Product.category))
    if active_only:
        query = query.where(Product.is_active.is_(True))
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    query = query.order_by(Product.id).offset(skip).limit(limit)
    return db.scalars(query).unique().all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
    )
    if not product:
        raise NotFoundError("Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    category = db.get(Category, payload.category_id)
    if not category:
        raise NotFoundError("Category not found")

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    product = db.scalar(
        select(Product).options(joinedload(Product.category)).where(Product.id == product.id)
    )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    product = db.get(Product, product_id)
    if not product:
        raise NotFoundError("Product not found")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        category = db.get(Category, data["category_id"])
        if not category:
            raise NotFoundError("Category not found")

    for key, value in data.items():
        setattr(product, key, value)

    db.commit()
    product = db.scalar(
        select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
    )
    return product


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    payload: StockUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    product = db.get(Product, product_id)
    if not product:
        raise NotFoundError("Product not found")

    product.stock = payload.stock
    db.commit()
    product = db.scalar(
        select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
    )
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    product = db.get(Product, product_id)
    if not product:
        raise NotFoundError("Product not found")
    # Soft delete to preserve order history
    product.is_active = False
    db.commit()
