import openai
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.config import settings
from app.utils.logger import get_logger

class OpenAIService:
    """Service d'intégration avec OpenAI GPT"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
    
    async def analyze_csv_data(
        self, 
        data_summary: Dict[str, Any], 
        user_question: str,
        analysis_type: str = "general",
        analysis_id: str = None
    ) -> Dict[str, Any]:
        """Analyse des données CSV avec GPT"""
        
        start_time = datetime.now()
        
        try:
            # Templates d'analyse par type
            templates = {
                "general": self._get_general_analysis_prompt(),
                "trends": self._get_trends_analysis_prompt(),
                "correlations": self._get_correlations_analysis_prompt(),
                "predictions": self._get_predictions_analysis_prompt(),
                "statistical": self._get_statistical_analysis_prompt()
            }
            
            prompt = templates.get(analysis_type, templates["general"])
            
            # Construction du prompt avec données
            full_prompt = f"""
{prompt}

DONNÉES À ANALYSER:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

QUESTION UTILISATEUR:
{user_question}

RÉPONSE ATTENDUE (JSON):
"""
            
            # Appel OpenAI
            response = await self._call_openai(full_prompt, analysis_id)
            
            # Parse de la réponse
            parsed_response = self._parse_analysis_response(response)
            
            # Calcul du temps de réponse
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Log de l'appel OpenAI
            if analysis_id:
                self.logger.log_openai_call(
                    analysis_id=analysis_id,
                    model=self.model,
                    tokens_used=parsed_response.get("tokens_used", 0),
                    response_time=response_time
                )
            
            return parsed_response
            
        except Exception as e:
            self.logger.log_error(
                error_type="openai_analysis_error",
                message=f"Erreur lors de l'analyse OpenAI: {str(e)}",
                analysis_id=analysis_id
            )
            return self._handle_analysis_error(e)
    
    def _get_general_analysis_prompt(self) -> str:
        return """
Tu es un expert en analyse de données et en business intelligence. Analyse les données CSV fournies et réponds à la question de l'utilisateur.

RÉGLES IMPORTANTES:
1. Réponds UNIQUEMENT en JSON valide
2. Sois précis, factuel et actionnable
3. Identifie les patterns, tendances et anomalies
4. Fournis des insights business concrets
5. Suggère des visualisations pertinentes
6. Évalue la qualité des données
7. Donne des recommandations pratiques

STRUCTURE DE RÉPONSE JSON:
{
    "summary": "Résumé exécutif en 2-3 phrases",
    "key_insights": [
        {
            "title": "Titre de l'insight",
            "description": "Description détaillée",
            "confidence": 0.85,
            "category": "trend|anomaly|correlation|business",
            "supporting_data": {"metric": "valeur"}
        }
    ],
    "anomalies": [
        {
            "type": "outlier|missing_data|inconsistency",
            "description": "Description de l'anomalie",
            "severity": "low|medium|high|critical",
            "affected_columns": ["col1", "col2"],
            "suggested_action": "Action recommandée"
        }
    ],
    "recommendations": [
        {
            "title": "Titre de la recommandation",
            "description": "Description détaillée",
            "priority": "low|medium|high|critical",
            "impact": "Impact attendu",
            "effort": "low|medium|high",
            "category": "data_quality|business|process"
        }
    ],
    "suggested_charts": [
        {
            "type": "line|bar|scatter|heatmap|histogram|box|pie",
            "title": "Titre du graphique",
            "description": "Description du graphique",
            "x_column": "colonne_x",
            "y_column": "colonne_y",
            "color_column": "colonne_couleur_optional"
        }
    ],
    "confidence_score": 0.85,
    "data_quality_score": 0.75,
    "tokens_used": 1500
}
"""
    
    def _get_trends_analysis_prompt(self) -> str:
        return """
Tu es un expert en analyse de tendances temporelles. Analyse les données pour identifier les tendances, saisonnalités et évolutions.

FOCUS SUR:
- Tendances temporelles (croissance, décroissance, stabilité)
- Saisonnalités et patterns cycliques
- Points de bascule et changements de tendance
- Projections et prévisions simples
- Comparaisons périodiques

STRUCTURE DE RÉPONSE JSON:
{
    "summary": "Résumé des tendances principales",
    "key_insights": [
        {
            "title": "Tendance identifiée",
            "description": "Description de la tendance",
            "confidence": 0.85,
            "category": "trend",
            "supporting_data": {
                "trend_direction": "up|down|stable",
                "trend_strength": "weak|moderate|strong",
                "period": "daily|weekly|monthly|yearly"
            }
        }
    ],
    "trends": [
        {
            "column": "nom_colonne",
            "direction": "up|down|stable",
            "strength": "weak|moderate|strong",
            "period": "daily|weekly|monthly|yearly",
            "description": "Description détaillée"
        }
    ],
    "suggested_charts": [
        {
            "type": "line",
            "title": "Évolution temporelle",
            "description": "Graphique de tendance",
            "x_column": "date_column",
            "y_column": "value_column"
        }
    ],
    "confidence_score": 0.85,
    "tokens_used": 1200
}
"""
    
    def _get_correlations_analysis_prompt(self) -> str:
        return """
Tu es un expert en analyse de corrélations et relations entre variables. Identifie les corrélations significatives et les relations causales potentielles.

FOCUS SUR:
- Corrélations positives et négatives
- Relations non-linéaires
- Variables explicatives
- Multicollinéarité
- Corrélations spurious

STRUCTURE DE RÉPONSE JSON:
{
    "summary": "Résumé des corrélations principales",
    "key_insights": [
        {
            "title": "Corrélation identifiée",
            "description": "Description de la relation",
            "confidence": 0.85,
            "category": "correlation",
            "supporting_data": {
                "correlation_strength": "weak|moderate|strong",
                "correlation_direction": "positive|negative",
                "variables": ["var1", "var2"]
            }
        }
    ],
    "correlations": [
        {
            "variable1": "col1",
            "variable2": "col2",
            "strength": "weak|moderate|strong",
            "direction": "positive|negative",
            "description": "Description de la relation"
        }
    ],
    "suggested_charts": [
        {
            "type": "scatter",
            "title": "Corrélation entre variables",
            "description": "Nuage de points",
            "x_column": "variable1",
            "y_column": "variable2"
        }
    ],
    "confidence_score": 0.85,
    "tokens_used": 1200
}
"""
    
    def _get_predictions_analysis_prompt(self) -> str:
        return """
Tu es un expert en prédiction et forecasting. Analyse les données pour identifier les patterns prédictifs et faire des projections.

FOCUS SUR:
- Patterns prédictifs dans les données
- Variables prédictives importantes
- Projections simples basées sur les tendances
- Facteurs de risque et incertitudes
- Recommandations pour améliorer la prédictibilité

STRUCTURE DE RÉPONSE JSON:
{
    "summary": "Résumé des insights prédictifs",
    "key_insights": [
        {
            "title": "Pattern prédictif",
            "description": "Description du pattern",
            "confidence": 0.85,
            "category": "prediction",
            "supporting_data": {
                "predictive_power": "low|medium|high",
                "time_horizon": "short|medium|long",
                "variables": ["var1", "var2"]
            }
        }
    ],
    "predictions": [
        {
            "target_variable": "variable_cible",
            "predictors": ["var1", "var2"],
            "prediction_horizon": "short|medium|long",
            "confidence_level": "low|medium|high",
            "description": "Description de la prédiction"
        }
    ],
    "suggested_charts": [
        {
            "type": "line",
            "title": "Projection temporelle",
            "description": "Graphique avec projection",
            "x_column": "date_column",
            "y_column": "value_column"
        }
    ],
    "confidence_score": 0.85,
    "tokens_used": 1200
}
"""
    
    def _get_statistical_analysis_prompt(self) -> str:
        return """
Tu es un expert en statistiques descriptives et inférentielles. Fournis une analyse statistique complète des données.

FOCUS SUR:
- Statistiques descriptives détaillées
- Distribution des variables
- Tests de normalité et outliers
- Intervalles de confiance
- Tests d'hypothèses appropriés

STRUCTURE DE RÉPONSE JSON:
{
    "summary": "Résumé statistique",
    "key_insights": [
        {
            "title": "Insight statistique",
            "description": "Description de l'insight",
            "confidence": 0.85,
            "category": "statistical",
            "supporting_data": {
                "statistic": "valeur",
                "p_value": 0.05,
                "significance": "significant|not_significant"
            }
        }
    ],
    "statistics": [
        {
            "variable": "nom_variable",
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0
        }
    ],
    "suggested_charts": [
        {
            "type": "histogram",
            "title": "Distribution",
            "description": "Histogramme de distribution",
            "x_column": "variable"
        }
    ],
    "confidence_score": 0.85,
    "tokens_used": 1200
}
"""
    
    async def _call_openai(self, prompt: str, analysis_id: str = None) -> str:
        """Appel OpenAI avec gestion d'erreurs"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en analyse de données. Réponds toujours en JSON valide et sois précis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except openai.RateLimitError as e:
            self.logger.log_error(
                error_type="openai_rate_limit",
                message=f"Rate limit OpenAI: {str(e)}",
                analysis_id=analysis_id
            )
            raise Exception("Limite de taux OpenAI atteinte. Réessayez plus tard.")
            
        except openai.AuthenticationError as e:
            self.logger.log_error(
                error_type="openai_auth_error",
                message=f"Erreur d'authentification OpenAI: {str(e)}",
                analysis_id=analysis_id
            )
            raise Exception("Erreur d'authentification OpenAI. Vérifiez la clé API.")
            
        except openai.APIError as e:
            self.logger.log_error(
                error_type="openai_api_error",
                message=f"Erreur API OpenAI: {str(e)}",
                analysis_id=analysis_id
            )
            raise Exception(f"Erreur API OpenAI: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                error_type="openai_unknown_error",
                message=f"Erreur inconnue OpenAI: {str(e)}",
                analysis_id=analysis_id
            )
            raise Exception(f"Erreur lors de l'appel OpenAI: {str(e)}")
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse OpenAI en JSON"""
        try:
            # Extraction du JSON de la réponse
            if response.strip().startswith('{') and response.strip().endswith('}'):
                json_str = response.strip()
            else:
                # Chercher le JSON dans la réponse
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                else:
                    raise ValueError("Aucun JSON trouvé dans la réponse")
            
            parsed = json.loads(json_str)
            
            # Validation de la structure
            required_fields = ["summary", "key_insights", "confidence_score"]
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = self._get_default_value(field)
            
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.log_error(
                error_type="json_parse_error",
                message=f"Erreur de parsing JSON: {str(e)}",
                details={"raw_response": response}
            )
            return self._create_fallback_response(response)
            
        except Exception as e:
            self.logger.log_error(
                error_type="response_parse_error",
                message=f"Erreur lors du parsing de la réponse: {str(e)}"
            )
            return self._create_fallback_response(response)
    
    def _get_default_value(self, field: str) -> Any:
        """Retourne une valeur par défaut pour un champ manquant"""
        defaults = {
            "summary": "Analyse effectuée avec succès",
            "key_insights": [],
            "anomalies": [],
            "recommendations": [],
            "suggested_charts": [],
            "confidence_score": 0.5,
            "data_quality_score": 0.5,
            "tokens_used": 0
        }
        return defaults.get(field, None)
    
    def _create_fallback_response(self, raw_response: str) -> Dict[str, Any]:
        """Crée une réponse de fallback en cas d'erreur de parsing"""
        return {
            "summary": "Analyse effectuée mais format de réponse inattendu",
            "key_insights": [
                {
                    "title": "Analyse basique",
                    "description": "L'analyse a été effectuée mais le format de réponse n'a pas pu être parsé correctement.",
                    "confidence": 0.3,
                    "category": "error"
                }
            ],
            "anomalies": [],
            "recommendations": [
                {
                    "title": "Vérifier les données",
                    "description": "Il est recommandé de vérifier la qualité et le format des données d'entrée.",
                    "priority": "medium",
                    "impact": "Amélioration de la qualité d'analyse",
                    "effort": "low",
                    "category": "data_quality"
                }
            ],
            "suggested_charts": [],
            "confidence_score": 0.3,
            "data_quality_score": 0.5,
            "tokens_used": 0,
            "raw_response": raw_response[:500] + "..." if len(raw_response) > 500 else raw_response
        }
    
    def _handle_analysis_error(self, error: Exception) -> Dict[str, Any]:
        """Gère les erreurs d'analyse"""
        return {
            "summary": f"Erreur lors de l'analyse: {str(error)}",
            "key_insights": [
                {
                    "title": "Erreur d'analyse",
                    "description": f"Une erreur s'est produite lors de l'analyse: {str(error)}",
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
            "suggested_charts": [],
            "confidence_score": 0.0,
            "data_quality_score": 0.0,
            "tokens_used": 0,
            "error": str(error)
        } 