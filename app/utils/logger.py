import logging
import json
import os
from datetime import datetime
from typing import Dict, Any
from app.config import settings

class StructuredLogger:
    """Logger structuré pour le monitoring du micro-service"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level))
        
        # Créer le dossier de logs si nécessaire
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        
        # Handler pour fichiers
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format structuré JSON
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Éviter les handlers dupliqués
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_analysis_start(self, analysis_id: str, user_id: str, file_count: int, question: str):
        """Log du début d'une analyse"""
        self.logger.info(json.dumps({
            "event": "analysis_started",
            "analysis_id": analysis_id,
            "user_id": user_id,
            "file_count": file_count,
            "question": question,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_analysis_complete(self, analysis_id: str, processing_time: float, success: bool, error: str = None):
        """Log de fin d'analyse"""
        log_data = {
            "event": "analysis_completed",
            "analysis_id": analysis_id,
            "processing_time": processing_time,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error:
            log_data["error"] = error
            
        self.logger.info(json.dumps(log_data))
    
    def log_openai_call(self, analysis_id: str, model: str, tokens_used: int, response_time: float):
        """Log des appels OpenAI"""
        self.logger.info(json.dumps({
            "event": "openai_call",
            "analysis_id": analysis_id,
            "model": model,
            "tokens_used": tokens_used,
            "response_time": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_privacy_event(self, analysis_id: str, event_type: str, details: Dict[str, Any]):
        """Log des événements de confidentialité"""
        self.logger.info(json.dumps({
            "event": "privacy_event",
            "analysis_id": analysis_id,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None, analysis_id: str = None):
        """Log d'erreur structuré"""
        log_data = {
            "event": "error",
            "error_type": error_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if analysis_id:
            log_data["analysis_id"] = analysis_id
            
        self.logger.error(json.dumps(log_data))
    
    def log_performance(self, operation: str, duration: float, analysis_id: str = None):
        """Log de performance"""
        log_data = {
            "event": "performance",
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if analysis_id:
            log_data["analysis_id"] = analysis_id
            
        self.logger.info(json.dumps(log_data))

    def log_info(self, message: str):
        """Log d'information simple"""
        self.logger.info(json.dumps({
            "event": "info",
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }))

    def log_warning(self, message: str):
        """Log d'avertissement simple"""
        self.logger.warning(json.dumps({
            "event": "warning",
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }))

def get_logger(name: str) -> StructuredLogger:
    """Factory pour créer un logger structuré"""
    return StructuredLogger(name) 