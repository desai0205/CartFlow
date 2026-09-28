import os

os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    user = User(
        email="user@example.com",
        full_name="Test User",
        hashed_password=hash_password("password123"),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin(db):
    admin_user = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user


@pytest.fixture
def user_token(client, user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": admin.email, "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_header(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def category(client, admin_header):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Gadgets"},
        headers=admin_header,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def product(client, admin_header, category):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Wireless Mouse",
            "description": "Ergonomic mouse",
            "price": "29.99",
            "stock": 50,
            "category_id": category["id"],
        },
        headers=admin_header,
    )
    assert response.status_code == 201
    return response.json()
