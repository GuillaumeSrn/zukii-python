"""
Routes API simplifiées pour MVP
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
import base64
from typing import List, Optional
import logging

from app.services.analysis_service import SimpleAnalysisService

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
analysis_service = SimpleAnalysisService()

@router.get("/health")
async def health_check():
    """Vérification de santé simplifiée"""
    return {
        "status": "healthy",
        "service": "python-analysis-service",
        "version": "1.0.0-mvp",
        "timestamp": "2025-08-02T18:00:00Z"
    }

@router.get("/capabilities")
async def get_capabilities():
    """Capacités du service simplifiées"""
    return {
        "supported_formats": ["csv", "xlsx"],
        "analysis_types": ["general"],
        "chart_types": ["bar", "line"],
        "max_file_size_mb": 50,
        "privacy_features": ["anonymization"],
        "openai_models": ["gpt-4o-mini"]
    }

@router.post("/analyze")
async def analyze_data(
    files: List[UploadFile] = File(...),
    question: str = Form(...),
    analysis_type: str = Form("general"),
    include_charts: bool = Form(True),
    anonymize_data: bool = Form(True)
):
    """Analyse de données simplifiée"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="Aucun fichier fourni")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        # Traitement des fichiers
        files_data = []
        for file in files:
            try:
                # Lire le contenu du fichier
                content = await file.read()
                
                # Décoder si nécessaire
                if file.filename.endswith('.csv'):
                    # Essayer différents encodages
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        raise ValueError(f"Impossible de décoder le fichier {file.filename}")
                elif file.filename.endswith('.xlsx'):
                    df = pd.read_excel(io.BytesIO(content))
                else:
                    raise ValueError(f"Format de fichier non supporté: {file.filename}")
                
                files_data.append((file.filename, df))
                
            except Exception as e:
                logger.error(f"Erreur lecture fichier {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Erreur lecture fichier {file.filename}: {str(e)}"
                )
        
        # Analyse
        if len(files_data) == 1:
            # Analyse d'un seul fichier
            filename, df = files_data[0]
            result = analysis_service.analyze_single_file(
                df=df,
                question=question,
                analysis_type=analysis_type,
                include_charts=include_charts,
                anonymize_data=anonymize_data
            )
        else:
            # Analyse de plusieurs fichiers
            result = await analysis_service.analyze_multiple_files(
                files_data=files_data,
                question=question,
                analysis_type=analysis_type,
                include_charts=include_charts,
                anonymize_data=anonymize_data
            )
        
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse: {str(e)}")
        return JSONResponse(
            content={
                "error": "Erreur interne du serveur",
                "details": str(e),
                "status": "error"
            },
            status_code=500
        )

@router.post("/analyze-base64")
async def analyze_data_base64(
    files_data: List[dict],
    question: str,
    analysis_type: str = "general",
    include_charts: bool = True,
    anonymize_data: bool = True
):
    """Analyse de données avec fichiers en base64"""
    try:
        if not files_data:
            raise HTTPException(status_code=400, detail="Aucun fichier fourni")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        # Traitement des fichiers base64
        processed_files = []
        for file_info in files_data:
            try:
                filename = file_info.get("filename", "unknown.csv")
                content_b64 = file_info.get("content", "")
                
                # Décoder base64
                content = base64.b64decode(content_b64)
                
                # Lire le DataFrame
                if filename.endswith('.csv'):
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        raise ValueError(f"Impossible de décoder le fichier {filename}")
                elif filename.endswith('.xlsx'):
                    df = pd.read_excel(io.BytesIO(content))
                else:
                    raise ValueError(f"Format de fichier non supporté: {filename}")
                
                processed_files.append((filename, df))
                
            except Exception as e:
                logger.error(f"Erreur lecture fichier {filename}: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur lecture fichier {filename}: {str(e)}"
                )
        
        # Analyse
        if len(processed_files) == 1:
            filename, df = processed_files[0]
            result = analysis_service.analyze_single_file(
                df=df,
                question=question,
                analysis_type=analysis_type,
                include_charts=include_charts,
                anonymize_data=anonymize_data
            )
        else:
            result = await analysis_service.analyze_multiple_files(
                files_data=processed_files,
                question=question,
                analysis_type=analysis_type,
                include_charts=include_charts,
                anonymize_data=anonymize_data
            )
        
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse base64: {str(e)}")
        return JSONResponse(
            content={
                "error": "Erreur interne du serveur",
                "details": str(e),
                "status": "error"
            },
            status_code=500
        ) 