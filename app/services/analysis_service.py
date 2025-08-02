import pandas as pd
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from app.utils.logger import get_logger
from app.utils.data_processor import DataProcessor
from app.services.anonymization_service import AnonymizationService
from app.services.openai_service import OpenAIService
from app.services.visualization_service import VisualizationService
from app.models.request_models import AnalysisRequest
from app.models.response_models import (
    AnalysisResponse, Insight, Anomaly, Recommendation, 
    ChartData, PrivacyReport, PerformanceMetrics
)

class AnalysisService:
    """Service principal d'analyse qui orchestre tous les autres services"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.data_processor = DataProcessor()
        self.anonymization_service = AnonymizationService()
        self.openai_service = OpenAIService()
        self.visualization_service = VisualizationService()
    
    def analyze_single_file(
        self,
        df: pd.DataFrame,
        question: str,
        analysis_type: str = "general",
        include_charts: bool = True,
        anonymize_data: bool = True,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyse d'un seul fichier (version synchrone simplifiée)
        
        Args:
            df: DataFrame pandas à analyser
            question: Question d'analyse de l'utilisateur
            analysis_type: Type d'analyse
            include_charts: Inclure des graphiques
            anonymize_data: Anonymiser les données
            conversation_id: ID de conversation pour la mémoire
            
        Returns:
            Dict contenant les résultats d'analyse
        """
        # Validation des données d'entrée
        if df is None:
            raise ValueError("DataFrame ne peut pas être None")
        
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Le paramètre df doit être un DataFrame pandas")
        
        if not question or not isinstance(question, str):
            raise ValueError("La question doit être une chaîne non vide")
        
        import asyncio
        
        # Exécuter la version asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._analyze_data_async(
                    df=df,
                    question=question,
                    analysis_type=analysis_type,
                    include_charts=include_charts,
                    anonymize_data=anonymize_data
                )
            )
        finally:
            loop.close()

    async def _analyze_data_async(
        self,
        df: pd.DataFrame,
        question: str,
        analysis_type: str = "general",
        include_charts: bool = True,
        anonymize_data: bool = True,
        analysis_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyse complète des données avec IA
        
        Args:
            df: DataFrame pandas à analyser
            question: Question d'analyse de l'utilisateur
            analysis_type: Type d'analyse (general, trends, correlations, predictions, statistical)
            include_charts: Inclure des graphiques dans la réponse
            anonymize_data: Anonymiser les données sensibles
            analysis_id: ID de l'analyse pour le tracking
            
        Returns:
            Dict contenant les résultats d'analyse complets
        """
        start_time = datetime.now()
        
        if not analysis_id:
            analysis_id = str(uuid.uuid4())
        
        try:
            self.logger.log_analysis_start(
                analysis_id=analysis_id,
                user_id="system",
                file_count=1,
                question=question
            )
            
            # 1. Préparation des données
            df_clean, data_summary = self.data_processor.prepare_data_for_analysis(df)
            
            # 2. Anonymisation si demandée
            anonymization_report = None
            if anonymize_data:
                df_clean, anonymization_report = self.anonymization_service.anonymize_dataframe(
                    df_clean, analysis_id
                )
            
            # 3. Analyse IA avec OpenAI
            openai_start = datetime.now()
            ai_analysis = await self.openai_service.analyze_csv_data(
                data_summary=data_summary,
                user_question=question,
                analysis_type=analysis_type,
                analysis_id=analysis_id
            )
            openai_time = (datetime.now() - openai_start).total_seconds()
            
            # 4. Génération des graphiques si demandée
            charts = []
            chart_generation_time = 0.0
            
            if include_charts and ai_analysis.get("suggested_charts"):
                chart_start = datetime.now()
                charts = await self._generate_charts(df_clean, ai_analysis, analysis_id)
                chart_generation_time = (datetime.now() - chart_start).total_seconds()
            
            # 5. Construction de la réponse finale
            total_time = (datetime.now() - start_time).total_seconds()
            
            response = self._build_analysis_response(
                analysis_id=analysis_id,
                ai_analysis=ai_analysis,
                data_summary=data_summary,
                charts=charts,
                anonymization_report=anonymization_report,
                performance_metrics={
                    "processing_time": total_time,
                    "openai_response_time": openai_time,
                    "chart_generation_time": chart_generation_time,
                    "tokens_used": ai_analysis.get("tokens_used", 0)
                }
            )
            
            # 6. Log de fin d'analyse
            self.logger.log_analysis_complete(
                analysis_id=analysis_id,
                processing_time=total_time,
                success=True
            )
            
            return response
            
        except Exception as e:
            error_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.log_analysis_complete(
                analysis_id=analysis_id,
                processing_time=error_time,
                success=False,
                error=str(e)
            )
            
            return self._build_error_response(analysis_id, str(e), error_time)
    
    async def _generate_charts(
        self, 
        df: pd.DataFrame, 
        ai_analysis: Dict[str, Any], 
        analysis_id: str
    ) -> List[Dict[str, Any]]:
        """Génère les graphiques basés sur les suggestions de l'IA"""
        charts = []
        suggested_charts = ai_analysis.get("suggested_charts", [])
        
        for i, chart_suggestion in enumerate(suggested_charts[:4]):  # Max 4 graphiques
            try:
                chart_config = {
                    "type": chart_suggestion.get("type", "line"),
                    "title": chart_suggestion.get("title", f"Graphique {i+1}"),
                    "description": chart_suggestion.get("description", ""),
                    "x_column": chart_suggestion.get("x_column"),
                    "y_column": chart_suggestion.get("y_column"),
                    "color_column": chart_suggestion.get("color_column"),
                    "width": 600,
                    "height": 400
                }
                
                chart_data = self.visualization_service.generate_chart(
                    df, chart_config, analysis_id
                )
                
                if not chart_data.get("error", False):
                    charts.append(chart_data)
                    
            except Exception as e:
                self.logger.log_error(
                    error_type="chart_generation_error",
                    message=f"Erreur lors de la génération du graphique {i+1}: {str(e)}",
                    analysis_id=analysis_id
                )
                continue
        
        return charts
    
    def _build_analysis_response(
        self,
        analysis_id: str,
        ai_analysis: Dict[str, Any],
        data_summary: Dict[str, Any],
        charts: List[Dict[str, Any]],
        anonymization_report: Optional[Dict[str, Any]],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construit la réponse d'analyse complète"""
        
        # Conversion des insights
        insights = []
        for insight_data in ai_analysis.get("key_insights", []):
            insight = Insight(
                title=insight_data.get("title", "Insight"),
                description=insight_data.get("description", ""),
                confidence=insight_data.get("confidence", 0.5),
                category=insight_data.get("category", "general"),
                supporting_data=insight_data.get("supporting_data")
            )
            insights.append(insight.dict())
        
        # Conversion des anomalies
        anomalies = []
        for anomaly_data in ai_analysis.get("anomalies", []):
            anomaly = Anomaly(
                type=anomaly_data.get("type", "unknown"),
                description=anomaly_data.get("description", ""),
                severity=anomaly_data.get("severity", "low"),
                affected_columns=anomaly_data.get("affected_columns", []),
                affected_rows=anomaly_data.get("affected_rows"),
                suggested_action=anomaly_data.get("suggested_action")
            )
            anomalies.append(anomaly.dict())
        
        # Conversion des recommandations
        recommendations = []
        for rec_data in ai_analysis.get("recommendations", []):
            recommendation = Recommendation(
                title=rec_data.get("title", "Recommandation"),
                description=rec_data.get("description", ""),
                priority=rec_data.get("priority", "medium"),
                impact=rec_data.get("impact", ""),
                effort=rec_data.get("effort", "medium"),
                category=rec_data.get("category", "general")
            )
            recommendations.append(recommendation.dict())
        
        # Conversion des graphiques
        chart_objects = []
        for chart_data in charts:
            chart = ChartData(
                type=chart_data.get("type", "line"),
                title=chart_data.get("title", "Graphique"),
                description=chart_data.get("description", ""),
                data=chart_data.get("data", {}),
                config=chart_data.get("config", {}),
                width=chart_data.get("width"),
                height=chart_data.get("height")
            )
            chart_objects.append(chart.dict())
        
        # Rapport de confidentialité
        privacy_report = PrivacyReport(
            anonymization_applied=anonymization_report is not None,
            sensitive_columns_detected=anonymization_report.get("sensitive_columns_detected", []) if anonymization_report else [],
            data_retention_days=30,
            compliance_status="compliant",
            data_processing_purpose="analyse_ia",
            data_controller="Zukii"
        )
        
        # Métriques de performance
        perf_metrics = PerformanceMetrics(
            processing_time=performance_metrics["processing_time"],
            openai_tokens_used=performance_metrics["tokens_used"],
            openai_response_time=performance_metrics["openai_response_time"],
            chart_generation_time=performance_metrics["chart_generation_time"]
        )
        
        # Construction de la réponse
        response = AnalysisResponse(
            analysis_id=analysis_id,
            summary=ai_analysis.get("summary", "Analyse effectuée"),
            key_insights=insights,
            anomalies=anomalies,
            recommendations=recommendations,
            charts=chart_objects,
            confidence_score=ai_analysis.get("confidence_score", 0.5),
            performance_metrics=perf_metrics.dict(),
            privacy_report=privacy_report.dict(),
            data_summary=data_summary
        )
        
        return response.dict()
    
    def _build_error_response(self, analysis_id: str, error_message: str, processing_time: float) -> Dict[str, Any]:
        """Construit une réponse d'erreur"""
        return {
            "analysis_id": analysis_id,
            "summary": f"Erreur lors de l'analyse: {error_message}",
            "key_insights": [
                {
                    "title": "Erreur d'analyse",
                    "description": f"Une erreur s'est produite: {error_message}",
                    "confidence": 0.0,
                    "category": "error"
                }
            ],
            "anomalies": [],
            "recommendations": [
                {
                    "title": "Résoudre l'erreur",
                    "description": "Vérifiez les données d'entrée et réessayez l'analyse.",
                    "priority": "high",
                    "impact": "Permettre l'analyse",
                    "effort": "medium",
                    "category": "error_resolution"
                }
            ],
            "charts": [],
            "confidence_score": 0.0,
            "performance_metrics": {
                "processing_time": processing_time,
                "openai_tokens_used": 0,
                "openai_response_time": 0.0,
                "chart_generation_time": 0.0
            },
            "privacy_report": {
                "anonymization_applied": False,
                "sensitive_columns_detected": [],
                "data_retention_days": 30,
                "compliance_status": "error",
                "data_processing_purpose": "analyse_ia",
                "data_controller": "Zukii"
            },
            "data_summary": {},
            "error": True,
            "error_message": error_message
        }
    
    async def analyze_multiple_files(
        self,
        files_data: List[Tuple[str, pd.DataFrame]],
        question: str,
        analysis_type: str = "general",
        include_charts: bool = True,
        anonymize_data: bool = True
    ) -> Dict[str, Any]:
        """
        Analyse de plusieurs fichiers en parallèle
        
        Args:
            files_data: Liste de tuples (filename, DataFrame)
            question: Question d'analyse
            analysis_type: Type d'analyse
            include_charts: Inclure des graphiques
            anonymize_data: Anonymiser les données
            
        Returns:
            Dict contenant l'analyse combinée
        """
        analysis_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            self.logger.log_analysis_start(
                analysis_id=analysis_id,
                user_id="system",
                file_count=len(files_data),
                question=question
            )
            
            # Combiner tous les DataFrames
            combined_df = pd.concat([df for _, df in files_data], ignore_index=True)
            
            # Ajouter une colonne pour identifier la source
            combined_df['source_file'] = [filename for filename, _ in files_data for _ in range(len(_))]
            
            # Analyser le DataFrame combiné
            result = await self.analyze_data(
                df=combined_df,
                question=question,
                analysis_type=analysis_type,
                include_charts=include_charts,
                anonymize_data=anonymize_data,
                analysis_id=analysis_id
            )
            
            # Ajouter des métadonnées sur les fichiers
            result["files_analyzed"] = [
                {
                    "filename": filename,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
                for filename, df in files_data
            ]
            
            return result
            
        except Exception as e:
            error_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.log_analysis_complete(
                analysis_id=analysis_id,
                processing_time=error_time,
                success=False,
                error=str(e)
            )
            
            return self._build_error_response(analysis_id, str(e), error_time) 