from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
import uuid
import time
from io import StringIO

from app.models.request_models import AnalysisRequest, BatchAnalysisRequest
from app.models.response_models import AnalysisResponse, ErrorResponse, HealthResponse, CapabilitiesResponse
from app.services.analysis_service import AnalysisService
from app.utils.security import validate_upload_file
from app.utils.data_processor import DataProcessor
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Services
analysis_service = AnalysisService()
data_processor = DataProcessor()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    question: str = Form(..., min_length=10, max_length=1000),
    analysis_type: str = Form(default="general"),
    include_charts: bool = Form(default=True),
    anonymize_data: bool = Form(default=True),
    background_tasks: BackgroundTasks = None
):
    """
    Analyse un fichier CSV avec IA
    
    - **file**: Fichier CSV à analyser
    - **question**: Question d'analyse (min 10 caractères)
    - **analysis_type**: Type d'analyse (general, trends, correlations, predictions, statistical)
    - **include_charts**: Inclure des graphiques dans la réponse
    - **anonymize_data**: Anonymiser les données sensibles
    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    try:
        logger.log_info(f"Début analyse {analysis_id}: {file.filename}")
        
        # Validation du fichier
        await validate_upload_file(file)
        
        # Lecture du CSV
        content = await file.read()
        df = data_processor.load_csv_from_bytes(content)
        
        # Analyse avec le service
        result = await analysis_service._analyze_data_async(
            df=df,
            question=question,
            analysis_type=analysis_type,
            include_charts=include_charts,
            anonymize_data=anonymize_data,
            analysis_id=analysis_id
        )
        
        processing_time = time.time() - start_time
        logger.log_info(f"Analyse {analysis_id} terminée en {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.log_error("analysis_error", f"Erreur analyse {analysis_id}: {str(e)}")
        
        error_response = ErrorResponse(
            error="analysis_error",
            message=f"Erreur lors de l'analyse: {str(e)}",
            details={"filename": file.filename, "processing_time": processing_time},
            analysis_id=analysis_id
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )

@router.post("/analyze/batch", response_model=AnalysisResponse)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...),
    question: str = Form(..., min_length=10, max_length=1000),
    analysis_type: str = Form(default="general"),
    include_charts: bool = Form(default=True),
    anonymize_data: bool = Form(default=True)
):
    """
    Analyse plusieurs fichiers CSV avec IA
    
    - **files**: Liste de fichiers CSV à analyser
    - **question**: Question d'analyse (min 10 caractères)
    - **analysis_type**: Type d'analyse
    - **include_charts**: Inclure des graphiques
    - **anonymize_data**: Anonymiser les données
    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    try:
        logger.log_info(f"Début analyse batch {analysis_id}: {len(files)} fichiers")
        
        files_data = []
        
        for file in files:
            # Validation du fichier
            await validate_upload_file(file)
            
            # Lecture du CSV
            content = await file.read()
            df = data_processor.load_csv_from_bytes(content)
            
            files_data.append((file.filename, df))
        
        # Analyse avec le service
        result = await analysis_service.analyze_multiple_files(
            files_data=files_data,
            question=question,
            analysis_type=analysis_type,
            include_charts=include_charts,
            anonymize_data=anonymize_data
        )
        
        processing_time = time.time() - start_time
        logger.log_info(f"Analyse batch {analysis_id} terminée en {processing_time:.2f}s")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.log_error("batch_analysis_error", f"Erreur analyse batch {analysis_id}: {str(e)}")
        
        error_response = ErrorResponse(
            error="batch_analysis_error",
            message=f"Erreur lors de l'analyse batch: {str(e)}",
            details={"file_count": len(files), "processing_time": processing_time},
            analysis_id=analysis_id
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Vérification de santé du service
    
    Retourne le statut du service et des dépendances
    """
    try:
        # Vérifier les dépendances
        openai_status = "healthy"
        try:
            # Test simple d'OpenAI (peut être optimisé)
            from app.services.openai_service import OpenAIService
            openai_service = OpenAIService()
            # Test minimal - pourrait être plus robuste
        except Exception as e:
            openai_status = f"error: {str(e)}"
        
        return HealthResponse(
            status="healthy",
            service="zukii-analysis",
            version="1.0.0",
            uptime=time.time(),  # Simplifié - devrait être calculé depuis le démarrage
            openai_status=openai_status
        )
        
    except Exception as e:
        logger.log_error("health_check_error", f"Erreur health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            service="zukii-analysis",
            version="1.0.0",
            openai_status="unknown"
        )

@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """
    Retourne les capacités du service
    
    Liste les fonctionnalités disponibles, formats supportés, etc.
    """
    return CapabilitiesResponse(
        supported_formats=["csv", "text/plain"],
        analysis_types=["general", "trends", "correlations", "predictions", "statistical"],
        chart_types=["line", "bar", "scatter", "heatmap", "histogram", "box", "pie"],
        max_file_size_mb=50,
        privacy_features=["anonymization", "data_retention", "gdpr_compliance"],
        openai_models=["gpt-4", "gpt-3.5-turbo"],
        rate_limits={
            "requests_per_minute": 60,
            "max_concurrent_analyses": 10,
            "max_file_size_mb": 50
        }
    )

@router.post("/validate")
async def validate_file(file: UploadFile = File(...)):
    """
    Valide un fichier sans l'analyser
    
    - **file**: Fichier à valider
    
    Retourne les informations de validation
    """
    try:
        # Validation du fichier
        await validate_upload_file(file)
        
        # Lecture et validation du contenu
        content = await file.read()
        df = data_processor.load_csv_from_bytes(content)
        
        return {
            "valid": True,
            "filename": file.filename,
            "file_size": len(content),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {str(col): int(count) for col, count in df.isnull().sum().items()}
        }
        
    except Exception as e:
        return {
            "valid": False,
            "filename": file.filename,
            "error": str(e)
        }

@router.get("/")
async def root():
    """
    Point d'entrée de l'API
    
    Retourne les informations de base sur le service
    """
    return {
        "service": "Zukii Analysis Service",
        "version": "1.0.0",
        "description": "Micro-service d'analyse IA pour fichiers CSV",
        "endpoints": {
            "analyze": "/analyze - Analyse un fichier CSV",
            "analyze_batch": "/analyze/batch - Analyse plusieurs fichiers",
            "health": "/health - Vérification de santé",
            "capabilities": "/capabilities - Capacités du service",
            "validate": "/validate - Validation de fichier"
        },
        "documentation": "/docs"
    } 