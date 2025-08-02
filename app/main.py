from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.utils.logger import get_logger

# Configuration du logger
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.log_info("🚀 Démarrage du service Zukii Analysis")
    logger.log_info(f"📊 Configuration: {settings.openai_model}, max_tokens={settings.openai_max_tokens}")
    logger.log_info(f"🔒 Anonymisation: {'activée' if settings.anonymization_enabled else 'désactivée'}")
    
    yield
    
    # Shutdown
    logger.log_info("🛑 Arrêt du service Zukii Analysis")

# Création de l'application FastAPI
app = FastAPI(
    title="Zukii Analysis Service",
    description="""
    Micro-service d'analyse IA pour fichiers CSV avec intégration OpenAI GPT.
    
    ## Fonctionnalités
    
    * **Analyse IA** : Analyse intelligente de données CSV avec GPT
    * **Visualisations** : Génération automatique de graphiques Plotly
    * **RGPD** : Anonymisation et protection des données sensibles
    * **Performance** : Monitoring et métriques détaillées
    
    ## Endpoints
    
    * `POST /analyze` - Analyse un fichier CSV
    * `POST /analyze/batch` - Analyse plusieurs fichiers
    * `GET /health` - Vérification de santé
    * `GET /capabilities` - Capacités du service
    * `POST /validate` - Validation de fichier
    """,
    version="1.0.0",
    contact={
        "name": "Zukii Team",
        "email": "contact@zukii.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # À configurer selon l'environnement
)

# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware pour logger les requêtes"""
    start_time = time.time()
    
    # Log de la requête
    logger.log_info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Calcul du temps de traitement
    process_time = time.time() - start_time
    
    # Log de la réponse
    logger.log_info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    # Ajouter le temps de traitement dans les headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Middleware de gestion d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global"""
    logger.log_error("global_error", f"❌ Erreur globale: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Erreur interne du serveur",
            "details": str(exc) if settings.api_debug else "Une erreur inattendue s'est produite",
            "timestamp": str(time.time())
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'erreurs HTTP"""
    logger.log_error("http_error", f"⚠️ Erreur HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(time.time())
        }
    )

# Inclusion des routes
app.include_router(router, prefix="/api/v1", tags=["analysis"])

# Route racine
@app.get("/")
async def root():
    """Point d'entrée principal"""
    return {
        "service": "Zukii Analysis Service",
        "version": "1.0.0",
        "status": "running",
        "description": "Micro-service d'analyse IA pour fichiers CSV",
        "endpoints": {
            "api": "/api/v1",
            "docs": "/docs",
            "health": "/api/v1/health",
            "capabilities": "/api/v1/capabilities"
        },
        "features": [
            "Analyse IA avec OpenAI GPT",
            "Visualisations Plotly",
            "Anonymisation RGPD",
            "Monitoring et métriques"
        ]
    }

# Route de santé simplifiée
@app.get("/health")
async def health():
    """Route de santé simple"""
    return {"status": "healthy", "service": "zukii-analysis"}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )