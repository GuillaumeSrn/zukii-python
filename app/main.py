"""
Application FastAPI simplifiée pour MVP
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router
from app.config import settings

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application
app = FastAPI(
    title="Zukii Analysis Service - MVP",
    description="Service d'analyse IA simplifié pour MVP",
    version="1.0.0-mvp"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour MVP, on autorise tout
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Point d'entrée principal"""
    return {
        "service": "Zukii Analysis Service - MVP",
        "version": "1.0.0-mvp",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "capabilities": "/api/v1/capabilities",
            "analyze": "/api/v1/analyze",
            "analyze-base64": "/api/v1/analyze-base64"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage"""
    logger.info("🚀 Service d'analyse Zukii MVP démarré")

@app.on_event("shutdown")
async def shutdown_event():
    """Événement d'arrêt"""
    logger.info("🛑 Service d'analyse Zukii MVP arrêté")