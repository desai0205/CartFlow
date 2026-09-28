"""Seed demo catalog data for the CartFlow UI."""
from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal, Base, engine
from app.models import Category, Product, User, UserRole


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.email == "admin@example.com"))
        if not admin:
            # Migrate older seed email if present
            legacy = db.scalar(select(User).where(User.email == "admin@cartflow.local"))
            if legacy:
                legacy.email = "admin@example.com"
                legacy.role = UserRole.ADMIN
                admin = legacy
                print("Updated admin email to admin@example.com / admin123")
            else:
                admin = User(
                    email="admin@example.com",
                    full_name="CartFlow Admin",
                    hashed_password=hash_password("admin123"),
                    role=UserRole.ADMIN,
                )
                db.add(admin)
                print("Created admin@example.com / admin123")
        else:
            admin.role = UserRole.ADMIN
            print("Admin already exists (role ensured)")

        if db.scalar(select(Category).limit(1)):
            db.commit()
            print("Catalog already seeded")
            return

        home = Category(name="Home", description="Everyday essentials")
        desk = Category(name="Desk", description="Tools for focused work")
        db.add_all([home, desk])
        db.flush()

        products = [
            Product(
                name="Ceramic Mug",
                description="Matte stoneware mug for slow mornings.",
                price="18.00",
                stock=40,
                category_id=home.id,
            ),
            Product(
                name="Linen Tea Towel",
                description="Soft, washable linen in forest green.",
                price="14.50",
                stock=55,
                category_id=home.id,
            ),
            Product(
                name="Desk Lamp",
                description="Warm adjustable light for late sessions.",
                price="49.00",
                stock=25,
                category_id=desk.id,
            ),
            Product(
                name="Notebook Set",
                description="Three ruled notebooks with stiff covers.",
                price="22.00",
                stock=60,
                category_id=desk.id,
            ),
            Product(
                name="Wireless Mouse",
                description="Quiet clicks, long battery life.",
                price="29.99",
                stock=35,
                category_id=desk.id,
            ),
        ]
        db.add_all(products)
        db.commit()
        print(f"Seeded {len(products)} products across 2 categories")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
