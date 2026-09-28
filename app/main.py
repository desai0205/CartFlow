from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.models import *  # noqa: F401, F403 — register models with metadata
from app.routers import auth, cart, categories, orders, products

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Skip auto-create during tests (they use their own SQLite engine)
    if os.getenv("TESTING") != "1":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "CartFlow — a lightweight e-commerce REST API with JWT auth, "
        "products, categories, cart, orders, and role-based access."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append(
            {
                "field": " → ".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg"),
                "type": err.get("type"),
            }
        )
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})


api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(categories.router, prefix=api_prefix)
app.include_router(products.router, prefix=api_prefix)
app.include_router(cart.router, prefix=api_prefix)
app.include_router(orders.router, prefix=api_prefix)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/api", tags=["Health"])
def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "ok",
    }


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Keep API docs and OpenAPI available
        if full_path.startswith(("api", "docs", "redoc", "openapi.json", "health")):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        index = FRONTEND_DIST / "index.html"
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(index)
else:

    @app.get("/", tags=["Health"])
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "status": "ok",
            "ui": "Run the frontend with: cd frontend && npm run dev",
        }
