from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_manager
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.schemas.health import HealthResponse
from app.utils.logger import logger

from app.api.auth import router as auth_router
from app.api.ai import router as ai_router
from app.api.eye_tracking import router as eye_tracking_router
from app.api.lip_reading import router as lip_reading_router
from app.api.sign_language import router as sign_language_router
from app.api.gpt import router as gpt_router
from app.api.emergency import router as emergency_router
from app.api.accessibility import router as accessibility_router
from app.api.intelligence import router as intelligence_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for managing startup & shutdown tasks.
    """
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    await db_manager.connect()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await db_manager.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI Accessibility Platform Backend powering Eye Tracking, Lip Reading, Sign Language decoding, and Emergency assistance.",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root API endpoint welcome information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health",
    }


# Top-level Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Server health check endpoint.
    Returns healthy status indication.
    """
    return HealthResponse(status="healthy")


# Mount API Routers
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(eye_tracking_router)
app.include_router(lip_reading_router)
app.include_router(sign_language_router)
app.include_router(gpt_router)
app.include_router(emergency_router)
app.include_router(accessibility_router)
app.include_router(intelligence_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
