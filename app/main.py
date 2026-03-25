from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stdout, 
    colorize=True, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Professional Redis OM Query Service for Sian Ecosystem",
        version="0.2.1",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting Sian Redis OM Service...")
        # Auto-migration on startup can be added here if desired
        # from app.services.migration_service import run_migrations
        # run_migrations()

    return app

app = create_app()
