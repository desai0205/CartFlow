from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise NotFoundError("Category not found")
    return category


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = db.scalar(select(Category).where(Category.name == payload.name))
    if existing:
        raise ConflictError("Category name already exists")

    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    category = db.get(Category, category_id)
    if not category:
        raise NotFoundError("Category not found")

    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        conflict = db.scalar(
            select(Category).where(Category.name == data["name"], Category.id != category_id)
        )
        if conflict:
            raise ConflictError("Category name already exists")

    for key, value in data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    category = db.get(Category, category_id)
    if not category:
        raise NotFoundError("Category not found")
    if category.products:
        raise ConflictError("Cannot delete category with products")
    db.delete(category)
    db.commit()
