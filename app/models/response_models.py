"""
Modèles de réponse simplifiés pour MVP
Version ultra-simplifiée sans validation Pydantic complexe
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

def create_simple_analysis_response(
    analysis_id: str,
    summary: str,
    insights: List[str],
    charts: List[Dict[str, Any]],
    anonymization_report: Optional[Dict[str, Any]] = None,
    processing_time: float = 0.0
) -> Dict[str, Any]:
    """Crée une réponse d'analyse simplifiée"""
    return {
        "analysis_id": analysis_id,
        "summary": summary,
        "insights": insights,
        "charts": charts,
        "anonymization_report": anonymization_report or {},
        "processing_time": processing_time,
        "created_at": datetime.utcnow().isoformat(),
        "status": "success"
    }

def create_multiple_files_response(
    analysis_id: str,
    files_analyzed: List[Dict[str, Any]],
    individual_results: List[Dict[str, Any]],
    total_files: int,
    successful_analyses: int,
    failed_analyses: int,
    processing_time: float
) -> Dict[str, Any]:
    """Crée une réponse pour plusieurs fichiers simplifiée"""
    return {
        "analysis_id": analysis_id,
        "summary": f"Analyse de {total_files} fichiers",
        "files_analyzed": files_analyzed,
        "individual_results": individual_results,
        "total_files": total_files,
        "successful_analyses": successful_analyses,
        "failed_analyses": failed_analyses,
        "processing_time": processing_time,
        "created_at": datetime.utcnow().isoformat(),
        "status": "success"
    }

def create_error_response(
    analysis_id: str,
    error_message: str,
    processing_time: float = 0.0
) -> Dict[str, Any]:
    """Crée une réponse d'erreur simplifiée"""
    return {
        "analysis_id": analysis_id,
        "error": error_message,
        "processing_time": processing_time,
        "created_at": datetime.utcnow().isoformat(),
        "status": "error"
    } 