from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class AnalysisType(str, Enum):
    """Types d'analyse disponibles"""
    GENERAL = "general"
    TRENDS = "trends"
    CORRELATIONS = "correlations"
    PREDICTIONS = "predictions"
    STATISTICAL = "statistical"

class ChartType(str, Enum):
    """Types de graphiques disponibles"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX = "box"
    PIE = "pie"

class AnalysisRequest(BaseModel):
    """Modèle de requête d'analyse"""
    question: str = Field(
        ..., 
        min_length=10, 
        max_length=1000,
        description="Question d'analyse à poser à l'IA"
    )
    analysis_type: AnalysisType = Field(
        default=AnalysisType.GENERAL,
        description="Type d'analyse à effectuer"
    )
    include_charts: bool = Field(
        default=True, 
        description="Inclure des graphiques dans la réponse"
    )
    anonymize_data: bool = Field(
        default=True, 
        description="Anonymiser les données sensibles"
    )
    chart_types: Optional[List[ChartType]] = Field(
        default=None, 
        description="Types de graphiques spécifiques souhaités"
    )
    max_charts: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Nombre maximum de graphiques à générer"
    )
    
    @validator('question')
    def validate_question(cls, v):
        """Valide la question d'analyse"""
        if len(v.strip()) < 10:
            raise ValueError('La question doit contenir au moins 10 caractères')
        if len(v.strip()) > 1000:
            raise ValueError('La question ne peut pas dépasser 1000 caractères')
        return v.strip()

class FileUploadRequest(BaseModel):
    """Modèle de requête d'upload de fichier"""
    filename: str = Field(
        ..., 
        description="Nom du fichier"
    )
    content_type: str = Field(
        ..., 
        description="Type MIME du fichier"
    )
    file_size: int = Field(
        ..., 
        gt=0, 
        le=52428800,  # 50MB
        description="Taille en bytes (max 50MB)"
    )
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Valide le type de contenu"""
        allowed_types = ['text/csv', 'application/csv', 'text/plain']
        if v not in allowed_types:
            raise ValueError(f'Type de fichier non supporté. Types autorisés: {", ".join(allowed_types)}')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        """Valide le nom de fichier"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Le nom de fichier ne peut pas être vide')
        if len(v) > 255:
            raise ValueError('Le nom de fichier ne peut pas dépasser 255 caractères')
        return v.strip()

class BatchAnalysisRequest(BaseModel):
    """Modèle pour l'analyse de plusieurs fichiers"""
    question: str = Field(..., description="Question d'analyse")
    analysis_type: AnalysisType = Field(default=AnalysisType.GENERAL)
    include_charts: bool = Field(default=True)
    anonymize_data: bool = Field(default=True)
    file_ids: List[str] = Field(..., min_items=1, max_items=10, description="IDs des fichiers à analyser")
    
    @validator('question')
    def validate_question(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('La question doit contenir au moins 10 caractères')
        return v.strip()

class AnalysisConfig(BaseModel):
    """Configuration avancée pour l'analyse"""
    openai_model: Optional[str] = Field(default=None, description="Modèle OpenAI à utiliser")
    max_tokens: Optional[int] = Field(default=None, ge=100, le=4000, description="Nombre max de tokens")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Température OpenAI")
    language: str = Field(default="fr", description="Langue de la réponse")
    include_code: bool = Field(default=False, description="Inclure du code dans la réponse")
    detailed_explanation: bool = Field(default=True, description="Explication détaillée") 