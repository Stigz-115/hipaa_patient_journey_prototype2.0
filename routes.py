import os
import sys

# Ensure project root is in path for backend imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.journey import router as journey_router
from backend.routers.attribution import router as attribution_router
from backend.routers.compliance import router as compliance_router


def create_app(static_dir: str) -> FastAPI:
    app = FastAPI(
        title="HIPAA-Safe Patient Journey Analytics",
        description="Privacy-compliant multi-touch attribution and patient journey analysis. Synthetic data only.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/api/health")
    def health():
        return {"ok": True, "phi_in_pipeline": False}

    # Domain routers
    app.include_router(journey_router)
    app.include_router(attribution_router)
    app.include_router(compliance_router)

    # SPA static file serving
    if os.path.isdir(static_dir):
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{path:path}")
        async def spa_fallback(request: Request, path: str):
            file_path = os.path.join(static_dir, path)
            if path and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(
                os.path.join(static_dir, "index.html"),
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )

    return app
