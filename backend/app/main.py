from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.cloud_sources import router as cloud_sources_router
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.core.config import settings

app = FastAPI(
    title="Madarik API",
    description="Madarik API with Phase 2 accounts and persistence foundation.",
    version="1.0.0-rc.1-phase2b1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(cloud_sources_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
