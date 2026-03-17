"""Main API v1 router that includes all sub-routers."""
from fastapi import APIRouter

from app.api.v1 import auth, configs, jobs, results, schedules, ws
from app.api.v1.health import router as health_router
from app.api.v1.metrics import router as metrics_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(configs.router, prefix="/configs", tags=["Scrape Configs"])
api_v1_router.include_router(health_router, prefix="/health", tags=["health"])
api_v1_router.include_router(jobs.router, prefix="/jobs", tags=["Scrape Jobs"])
api_v1_router.include_router(metrics_router, prefix="/metrics", tags=["monitoring"])
api_v1_router.include_router(results.router, prefix="/results", tags=["Scraped Results"])
api_v1_router.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
api_v1_router.include_router(ws.router, prefix="/ws", tags=["WebSocket"])
