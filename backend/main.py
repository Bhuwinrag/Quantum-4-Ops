"""
QUANTUM//OPS - Quantum Hybrid Computing Workbench
Main FastAPI Application Server
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.schemas import (
    CommandRequest, CommandResponse, SystemInfoResponse,
    ModuleStatusResponse, ModuleExecutionResponse
)
from backend.module_registry import registry
from backend.command_handler import CommandHandler
from backend.system_info import get_full_system_info
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    logger.info("QUANTUM//OPS Hybrid Workbench Server starting up...")
    registry.initialize()
    logger.info("Module Registry initialized. 4 Module slots active.")
    yield
    logger.info("QUANTUM//OPS Hybrid Workbench Server shutting down.")


app = FastAPI(
    title="QUANTUM//OPS Backend",
    description="Quantum Hybrid Computing Workbench API",
    version="1.0.0-PROD",
    lifespan=lifespan,
)

# CORS Configuration
origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Returns SVG favicon to eliminate 404 warnings."""
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="10" fill="#00FF41" />
        <ellipse cx="50" cy="50" rx="42" ry="16" fill="none" stroke="#00FFFF" stroke-width="3" transform="rotate(30 50 50)" />
        <ellipse cx="50" cy="50" rx="42" ry="16" fill="none" stroke="#00FF41" stroke-width="3" transform="rotate(90 50 50)" />
        <ellipse cx="50" cy="50" rx="42" ry="16" fill="none" stroke="#00FFFF" stroke-width="3" transform="rotate(150 50 50)" />
    </svg>"""
    return Response(content=svg_icon, media_type="image/svg+xml")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "QUANTUM//OPS",
        "version": "1.0.0-PROD",
    }


@app.get("/api/system/info", response_model=SystemInfoResponse)
async def system_info():
    """Returns aggregated system hardware and platform telemetry."""
    summary = registry.get_status_summary()
    return get_full_system_info(summary)


@app.get("/api/modules")
async def list_modules():
    """Returns discovery status for all registered modules."""
    statuses = registry.get_all_statuses()
    return {k: v.model_dump() for k, v in statuses.items()}


@app.get("/api/modules/{module_name}/status", response_model=ModuleStatusResponse)
async def get_module_status(module_name: str):
    """Queries detailed status for a single module."""
    mod = registry.get(module_name)
    if not mod:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{module_name}' not found. Available: cudaq, qiskit, nvqlink, shor"
        )
    return mod.query_status()


@app.post("/api/execute", response_model=CommandResponse)
async def execute_command(req: CommandRequest):
    """Executes a command string received from the frontend terminal."""
    command_text = req.raw_input or (f"{req.command} {' '.join(req.args)}".strip())
    response = await CommandHandler.process(command_text)
    return response


# Static Frontend Hosting
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
src_dir = os.path.join(frontend_dir, "src")

if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    if os.path.isdir(src_dir):
        app.mount("/src", StaticFiles(directory=src_dir), name="src")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"message": "QUANTUM//OPS Backend Running. Frontend index.html not found."}


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
