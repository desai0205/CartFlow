# CartFlow

A small e-commerce stack: **FastAPI + PostgreSQL + JWT API** and a **React shop UI**.

## Features

- User registration & login (JWT)
- Admin / user roles
- Categories & products (CRUD)
- Shopping cart
- Create & view orders
- Basic stock management
- Validation, error handling, Swagger docs
- Storefront UI (home, shop, cart, orders, admin)

## Project structure

```
CartFlow/
├── app/                     # FastAPI backend
├── frontend/                # React (Vite) storefront
├── scripts/seed.py          # Demo admin + products
├── tests/
├── requirements.txt
└── .env.example
```

## Setup

### 1. Create database

```bash
createdb cartflow
# or via psql:
# CREATE DATABASE cartflow;
```

### 2. Install backend dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit DATABASE_URL and SECRET_KEY
```

### 4. Seed demo data (optional)

```bash
python -m scripts.seed
```

Creates:
- Admin: `admin@example.com` / `admin123`
- Sample categories & products

### 5. Run API + UI

Terminal 1 — API:

```bash
uvicorn app.main:app --reload
```

Terminal 2 — UI:

```bash
cd frontend
npm install
npm run dev
```

- **Shop UI:** http://127.0.0.1:5173
- **API docs:** http://127.0.0.1:8000/docs
- **Health:** http://127.0.0.1:8000/health

Or build the UI and serve it from FastAPI on port 8000:

```bash
cd frontend && npm run build
uvicorn app.main:app --reload
# open http://127.0.0.1:8000
```

## Creating an admin user

Use the seed script, or register then promote:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

## API overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register user |
| POST | `/api/v1/auth/login` | — | Login (form: username=email, password) |
| GET | `/api/v1/auth/me` | User | Current user |
| GET/POST | `/api/v1/categories` | Admin for write | List / create categories |
| GET/PUT/DELETE | `/api/v1/categories/{id}` | Admin for write | Category detail / update / delete |
| GET/POST | `/api/v1/products` | Admin for write | List / create products |
| GET/PUT/DELETE | `/api/v1/products/{id}` | Admin for write | Product detail / update / soft-delete |
| PATCH | `/api/v1/products/{id}/stock` | Admin | Update stock |
| GET | `/api/v1/cart` | User | View cart |
| POST | `/api/v1/cart/items` | User | Add item |
| PUT/DELETE | `/api/v1/cart/items/{id}` | User | Update / remove item |
| DELETE | `/api/v1/cart` | User | Clear cart |
| POST | `/api/v1/orders` | User | Checkout (from cart) |
| GET | `/api/v1/orders` | User/Admin | List own orders (admin: all) |
| GET | `/api/v1/orders/{id}` | User/Admin | Order detail |
| PATCH | `/api/v1/orders/{id}/status` | Admin | Update order status |

## Tests

Tests use an in-memory SQLite database (no PostgreSQL required):

```bash
pytest -v
```

## Notes

- Product delete is a soft delete (`is_active=false`) to preserve order history.
- Cancelling an order restores stock.
- Login uses OAuth2 password form (`username` = email) for Swagger Authorize support.
