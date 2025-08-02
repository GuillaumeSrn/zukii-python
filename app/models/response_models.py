from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .request_models import ChartType

class ChartData(BaseModel):
    """Données d'un graphique Plotly"""
    type: ChartType = Field(..., description="Type de graphique")
    title: str = Field(..., description="Titre du graphique")
    description: str = Field(..., description="Description du graphique")
    data: Dict[str, Any] = Field(..., description="Données Plotly JSON")
    config: Dict[str, Any] = Field(
        default_factory=lambda: {"displayModeBar": True, "responsive": True},
        description="Configuration Plotly"
    )
    width: Optional[int] = Field(default=None, description="Largeur du graphique")
    height: Optional[int] = Field(default=None, description="Hauteur du graphique")

class Insight(BaseModel):
    """Insight découvert par l'IA"""
    title: str = Field(..., description="Titre de l'insight")
    description: str = Field(..., description="Description détaillée")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Niveau de confiance")
    category: str = Field(..., description="Catégorie de l'insight")
    supporting_data: Optional[Dict[str, Any]] = Field(default=None, description="Données supportant l'insight")

class Anomaly(BaseModel):
    """Anomalie détectée dans les données"""
    type: str = Field(..., description="Type d'anomalie")
    description: str = Field(..., description="Description de l'anomalie")
    severity: str = Field(..., description="Sévérité (low, medium, high, critical)")
    affected_columns: List[str] = Field(default_factory=list, description="Colonnes affectées")
    affected_rows: Optional[List[int]] = Field(default=None, description="Lignes affectées")
    suggested_action: Optional[str] = Field(default=None, description="Action suggérée")

class Recommendation(BaseModel):
    """Recommandation basée sur l'analyse"""
    title: str = Field(..., description="Titre de la recommandation")
    description: str = Field(..., description="Description détaillée")
    priority: str = Field(..., description="Priorité (low, medium, high, critical)")
    impact: str = Field(..., description="Impact attendu")
    effort: str = Field(..., description="Effort requis (low, medium, high)")
    category: str = Field(..., description="Catégorie de recommandation")

class PrivacyReport(BaseModel):
    """Rapport de confidentialité RGPD"""
    anonymization_applied: bool = Field(..., description="Anonymisation appliquée")
    sensitive_columns_detected: List[str] = Field(default_factory=list, description="Colonnes sensibles détectées")
    data_retention_days: int = Field(..., description="Durée de rétention en jours")
    compliance_status: str = Field(..., description="Statut de conformité RGPD")
    data_processing_purpose: str = Field(..., description="Finalité du traitement")
    data_controller: str = Field(default="Zukii", description="Responsable du traitement")

class PerformanceMetrics(BaseModel):
    """Métriques de performance de l'analyse"""
    processing_time: float = Field(..., description="Temps de traitement en secondes")
    openai_tokens_used: int = Field(..., description="Tokens OpenAI utilisés")
    openai_response_time: float = Field(..., description="Temps de réponse OpenAI")
    chart_generation_time: float = Field(..., description="Temps de génération des graphiques")
    memory_usage_mb: Optional[float] = Field(default=None, description="Utilisation mémoire en MB")

class AnalysisResponse(BaseModel):
    """Réponse d'analyse complète"""
    analysis_id: str = Field(..., description="ID unique de l'analyse")
    summary: str = Field(..., description="Résumé exécutif")
    key_insights: List[Insight] = Field(..., description="Insights clés")
    anomalies: List[Anomaly] = Field(default_factory=list, description="Anomalies détectées")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Recommandations")
    charts: List[ChartData] = Field(default_factory=list, description="Graphiques générés")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Score de confiance global")
    performance_metrics: PerformanceMetrics = Field(..., description="Métriques de performance")
    privacy_report: PrivacyReport = Field(..., description="Rapport de confidentialité")
    data_summary: Dict[str, Any] = Field(..., description="Résumé des données analysées")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Date de création")

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Détails supplémentaires")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp de l'erreur")
    analysis_id: Optional[str] = Field(default=None, description="ID de l'analyse si applicable")

class HealthResponse(BaseModel):
    """Réponse de vérification de santé"""
    status: str = Field(..., description="Statut du service")
    service: str = Field(..., description="Nom du service")
    version: str = Field(..., description="Version du service")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp")
    uptime: Optional[float] = Field(default=None, description="Temps de fonctionnement en secondes")
    openai_status: Optional[str] = Field(default=None, description="Statut de l'API OpenAI")

class CapabilitiesResponse(BaseModel):
    """Réponse des capacités du service"""
    supported_formats: List[str] = Field(..., description="Formats de fichiers supportés")
    analysis_types: List[str] = Field(..., description="Types d'analyse disponibles")
    chart_types: List[str] = Field(..., description="Types de graphiques disponibles")
    max_file_size_mb: int = Field(..., description="Taille maximale de fichier")
    privacy_features: List[str] = Field(..., description="Fonctionnalités de confidentialité")
    openai_models: List[str] = Field(..., description="Modèles OpenAI disponibles")
    rate_limits: Dict[str, Any] = Field(..., description="Limites de taux") 