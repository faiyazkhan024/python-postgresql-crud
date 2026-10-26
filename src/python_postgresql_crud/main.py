"""Main FastAPI application entrypoint, lifespan manager, and web UI routes."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from python_postgresql_crud.api import api_router
from python_postgresql_crud.config import get_settings
from python_postgresql_crud.database import db
from python_postgresql_crud.models import POPULAR_HOBBIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("python_postgresql_crud")

settings = get_settings()

_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
_TEMPLATES_DIR = _BASE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan manager to handle DB connection pool lifecycle."""
    logger.info("Starting %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    try:
        db.initialize_pool()
        db.init_db()
        logger.info("PostgreSQL database initialized successfully.")
    except Exception as exc:
        logger.warning(
            "Could not connect to PostgreSQL on startup (service may still be starting): %s",
            exc,
        )

    yield

    logger.info("Shutting down application and draining database connection pool...")
    db.close_pool()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-ready CRUD application demonstrating Python 3.13, "
        "FastAPI, and PostgreSQL integration with strict schema validation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets directory if it exists
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=_TEMPLATES_DIR) if _TEMPLATES_DIR.exists() else None


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> Any:
    """Render the main CRUD interactive user interface."""
    if templates is None:
        return HTMLResponse("<h1>Templates directory not found</h1>", status_code=500)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "popular_hobbies": POPULAR_HOBBIES,
            "debug": settings.DEBUG,
        },
    )


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    """Health check endpoint reporting service and database connection status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "connected" if db.is_connected else "disconnected",
    }


# Include API v1 router
app.include_router(api_router)


def run() -> None:
    """Entry point invoked by `python-postgresql-crud` console script."""
    uvicorn.run(
        "python_postgresql_crud.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run()
