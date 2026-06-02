from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from models import models
from core.config import settings
from core.logging_config import setup_logging, logger

# Initialize professional logging
setup_logging()
logger.info("Starting QAInspect Pro Backend Engine...")

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Intelligence & Test Management Suite",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# Configure CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api import scan
from api import dashboard
from api import testcases
from api import reports
from api import auth

@app.get("/")
def read_root():
    return {"status": "ok", "message": "QAInspect Pro Backend is running"}

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(dashboard.router)
app.include_router(testcases.router)
app.include_router(reports.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
