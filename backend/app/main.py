from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.cloud_sources import router as cloud_sources_router
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.core.config import settings
from app.core.release import APP_VERSION, RELEASE_PHASE, RELEASE_TITLE

app = FastAPI(
    title="Madarik API",
    description=(
        f"Madarik API. {RELEASE_PHASE}: {RELEASE_TITLE}."
    ),
    version=APP_VERSION,
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
