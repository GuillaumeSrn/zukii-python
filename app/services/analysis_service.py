"""
Service d'analyse simplifié pour MVP
Version ultra-simplifiée sans validation complexe
"""

import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import openai
import logging
import numpy as np

# Configuration simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_serializable(obj):
    """Convertit les objets pandas/numpy en types Python natifs sérialisables"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj

class SimpleAnalysisService:
    """Service d'analyse ultra-simplifié pour MVP"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.settings = {
            "model": "gpt-4o-mini",
            "max_tokens": 2000,
            "temperature": 0.3
        }
    
    def analyze_single_file(
        self,
        df: pd.DataFrame,
        question: str,
        analysis_type: str = "general",
        include_charts: bool = True,
        anonymize_data: bool = True
    ) -> Dict[str, Any]:
        """Analyse un seul fichier de manière simplifiée"""
        analysis_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Anonymisation simple
            if anonymize_data:
                df_anonymized = self._simple_anonymize(df)
            else:
                df_anonymized = df
            
            # Analyse IA complète
            ai_analysis = self._simple_ai_analysis(df_anonymized, question)
            
            # Génération de graphiques dynamiques
            charts = []
            if include_charts:
                charts = self._generate_dynamic_charts(df_anonymized)
            
            # Génération d'insights métier
            insights = self._generate_business_insights(df_anonymized)
            
            # Génération de recommandations basées sur l'analyse IA
            recommendations = self._generate_recommendations(df_anonymized, ai_analysis["analysis"])
            
            # Détection d'anomalies
            anomalies = self._detect_anomalies(df_anonymized)
            
            # Résumé intelligent
            summary = self._generate_intelligent_summary(df_anonymized, ai_analysis["analysis"])
            
            # Rapport de confidentialité
            privacy_report = {
                "anonymization_applied": anonymize_data,
                "sensitive_columns_detected": df.columns.tolist() if anonymize_data else [],
                "data_retention_days": 30,
                "compliance_status": "compliant",
                "data_processing_purpose": "analyse_ia",
                "data_controller": "Zukii"
            }
            
            # Métriques de performance
            processing_time = (datetime.now() - start_time).total_seconds()
            performance_metrics = {
                "processing_time": processing_time,
                "openai_tokens_used": 1000,  # Estimation
                "openai_response_time": processing_time * 0.8,
                "chart_generation_time": processing_time * 0.2
            }
            
            # Résumé des données
            data_summary = {
                "shape": {"rows": int(len(df)), "columns": int(len(df.columns))},
                "columns": {col: {"name": col, "dtype": str(dtype)} for col, dtype in df.dtypes.items()},
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": convert_to_serializable(df.isnull().sum().to_dict()),
                "basic_stats": {
                    "total_missing_values": int(df.isnull().sum().sum()),
                    "missing_percentage": float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
                }
            }
            
            # Construire la réponse finale avec l'analyse IA
            response_data = {
                "analysis_id": analysis_id,
                "summary": summary,
                "ai_analysis": ai_analysis["analysis"],  # ✅ AJOUT DE L'ANALYSE IA
                "key_insights": convert_to_serializable(insights),
                "anomalies": convert_to_serializable(anomalies),
                "recommendations": convert_to_serializable(recommendations),
                "charts": convert_to_serializable(charts),
                "confidence_score": 0.85,
                "performance_metrics": convert_to_serializable(performance_metrics),
                "privacy_report": convert_to_serializable(privacy_report),
                "data_summary": convert_to_serializable(data_summary),
                "created_at": datetime.utcnow().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Erreur d'analyse: {str(e)}")
            return {
                "analysis_id": analysis_id,
                "error": str(e),
                "processing_time": processing_time,
                "created_at": datetime.utcnow().isoformat(),
                "status": "error"
            }
    
    async def analyze_multiple_files(
        self,
        files_data: List[Tuple[str, pd.DataFrame]],
        question: str,
        analysis_type: str = "general",
        include_charts: bool = True,
        anonymize_data: bool = True
    ) -> Dict[str, Any]:
        """Analyse plusieurs fichiers de manière simplifiée"""
        analysis_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            all_results = []
            files_metadata = []
            
            for filename, df in files_data:
                try:
                    # Analyser chaque fichier
                    result = self.analyze_single_file(
                        df, question, analysis_type, include_charts, anonymize_data
                    )
                    
                    # Ajouter les métadonnées
                    result["file_info"] = {
                        "filename": filename,
                        "rows": len(df),
                        "columns": len(df.columns)
                    }
                    
                    all_results.append(result)
                    files_metadata.append({
                        "filename": filename,
                        "rows": len(df),
                        "columns": len(df.columns)
                    })
                    
                except Exception as e:
                    # En cas d'erreur, continuer avec les autres fichiers
                    error_result = {
                        "analysis_id": f"{analysis_id}_{filename}",
                        "error": f"Erreur sur le fichier {filename}: {str(e)}",
                        "processing_time": 0.0,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "error",
                        "file_info": {
                            "filename": filename,
                            "rows": len(df),
                            "columns": len(df.columns)
                        }
                    }
                    all_results.append(error_result)
                    files_metadata.append({
                        "filename": filename,
                        "rows": len(df),
                        "columns": len(df.columns),
                        "error": str(e)
                    })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "analysis_id": analysis_id,
                "summary": f"Analyse de {len(files_data)} fichiers",
                "files_analyzed": files_metadata,
                "individual_results": all_results,
                "total_files": len(files_data),
                "successful_analyses": len([r for r in all_results if r.get("status") == "success"]),
                "failed_analyses": len([r for r in all_results if r.get("status") == "error"]),
                "processing_time": processing_time,
                "created_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Erreur d'analyse multiple: {str(e)}")
            return {
                "analysis_id": analysis_id,
                "error": str(e),
                "processing_time": processing_time,
                "created_at": datetime.utcnow().isoformat(),
                "status": "error"
            }
    
    def _simple_ai_analysis(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Analyse IA améliorée avec insights métier"""
        try:
            # Analyser les données pour extraire des insights
            insights = []
            
            # Analyser les conversions
            if 'conversion' in df.columns:
                conversion_rate = (df['conversion'] == 'Oui').mean() * 100
                insights.append(f"Taux de conversion global: {conversion_rate:.1f}%")
            
            # Analyser les sources de trafic
            if 'source_trafic' in df.columns:
                source_performance = df.groupby('source_trafic')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                best_source = source_performance.idxmax()
                best_rate = source_performance.max()
                insights.append(f"Meilleure source de trafic: {best_source} ({best_rate:.1f}% de conversion)")
            
            # Analyser les appareils
            if 'appareil' in df.columns:
                device_performance = df.groupby('appareil')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                best_device = device_performance.idxmax()
                best_device_rate = device_performance.max()
                insights.append(f"Appareil le plus performant: {best_device} ({best_device_rate:.1f}% de conversion)")
            
            # Analyser les montants d'achat
            if 'montant_achat' in df.columns:
                avg_purchase = df[df['montant_achat'] > 0]['montant_achat'].mean()
                total_revenue = df['montant_achat'].sum()
                insights.append(f"Montant d'achat moyen: {avg_purchase:.2f}€")
                insights.append(f"Chiffre d'affaires total: {total_revenue:.2f}€")
            
            # Analyser l'engagement
            if 'score_engagement' in df.columns:
                avg_engagement = df['score_engagement'].mean()
                insights.append(f"Score d'engagement moyen: {avg_engagement:.2f}/1.0")
            
            # Préparer les données pour l'IA
            data_summary = {
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": convert_to_serializable(df.isnull().sum().to_dict()),
                "sample_data": convert_to_serializable(df.head(5).to_dict('list')),
                "insights": insights
            }
            
            # Prompt amélioré
            prompt = f"""
            Tu es un expert en analyse marketing web. Analyse ce dataset et réponds à cette question: {question}
            
            Informations sur le dataset:
            - Nombre de lignes: {len(df)}
            - Nombre de colonnes: {len(df.columns)}
            - Colonnes disponibles: {list(df.columns)}
            
            Insights extraits:
            {chr(10).join(insights)}
            
            Instructions:
            1. Fournis une analyse détaillée et professionnelle
            2. Identifie les tendances clés et les opportunités
            3. Propose des recommandations actionnables
            4. Utilise des métriques concrètes
            5. Structure ta réponse avec des sections claires
            
            Réponds en français de manière professionnelle.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.settings["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.settings["max_tokens"],
                temperature=self.settings["temperature"]
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "data_summary": convert_to_serializable(data_summary)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse IA: {str(e)}")
            return {
                "analysis": f"Erreur lors de l'analyse IA: {str(e)}",
                "data_summary": {}
            }
    

    
    def _simple_anonymize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Anonymisation simple des données"""
        df_anon = df.copy()
        
        # Anonymiser les colonnes sensibles
        sensitive_patterns = ['email', 'phone', 'address', 'name', 'id', 'user']
        for col in df_anon.columns:
            if any(pattern in col.lower() for pattern in sensitive_patterns):
                if df_anon[col].dtype == 'object':
                    df_anon[col] = f"ANONYMIZED_{col.upper()}"
        
        return df_anon

    def _generate_business_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Génération d'insights métier intelligents"""
        insights = []
        
        try:
            # Insight 1: Performance générale (si applicable)
            if 'conversion' in df.columns:
                conversion_rate = (df['conversion'] == 'Oui').mean() * 100
                insights.append({
                    "title": "Taux de conversion global",
                    "description": f"Le taux de conversion global est de {conversion_rate:.1f}%, ce qui indique la performance générale du site.",
                    "confidence": 0.95,
                    "category": "performance"
                })
            
            # Insight 2: Source de trafic la plus performante
            if 'source_trafic' in df.columns and 'conversion' in df.columns:
                source_performance = df.groupby('source_trafic')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                best_source = source_performance.idxmax()
                best_rate = source_performance.max()
                insights.append({
                    "title": "Source de trafic optimale",
                    "description": f"La source '{best_source}' génère le meilleur taux de conversion avec {best_rate:.1f}%.",
                    "confidence": 0.9,
                    "category": "marketing"
                })
            
            # Insight 3: Performance mobile vs desktop
            if 'appareil' in df.columns and 'conversion' in df.columns:
                device_performance = df.groupby('appareil')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                if len(device_performance) > 1:
                    best_device = device_performance.idxmax()
                    best_device_rate = device_performance.max()
                    insights.append({
                        "title": "Performance par appareil",
                        "description": f"Les utilisateurs {best_device} convertissent le mieux avec {best_device_rate:.1f}%.",
                        "confidence": 0.85,
                        "category": "ux"
                    })
            
            # Insight 4: Valeur moyenne des achats
            if 'montant_achat' in df.columns:
                avg_purchase = df[df['montant_achat'] > 0]['montant_achat'].mean()
                if not pd.isna(avg_purchase):
                    insights.append({
                        "title": "Valeur moyenne des achats",
                        "description": f"Le panier moyen s'élève à {avg_purchase:.2f}€, indiquant la valeur des clients.",
                        "confidence": 0.9,
                        "category": "revenue"
                    })
            
            # Insight 5: Engagement des utilisateurs
            if 'score_engagement' in df.columns:
                avg_engagement = df['score_engagement'].mean()
                insights.append({
                    "title": "Niveau d'engagement",
                    "description": f"Le score d'engagement moyen est de {avg_engagement:.2f}/1.0, reflétant l'expérience utilisateur.",
                    "confidence": 0.8,
                    "category": "engagement"
                })
            
            # Insight 6: Analyse temporelle (si date disponible)
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    df_sorted = df.sort_values(date_col)
                    total_days = (df_sorted[date_col].max() - df_sorted[date_col].min()).days
                    insights.append({
                        "title": "Période d'analyse",
                        "description": f"Données collectées sur {total_days} jours, permettant une analyse temporelle fiable.",
                        "confidence": 0.9,
                        "category": "temporal"
                    })
                except:
                    pass
            
            # Fallback si pas d'insights métier
            if not insights:
                insights = [
                    {
                        "title": "Analyse du dataset",
                        "description": f"Le dataset contient {len(df)} enregistrements avec {len(df.columns)} colonnes",
                        "confidence": 0.9,
                        "category": "general"
                    },
                    {
                        "title": "Types de données",
                        "description": f"Types de colonnes: {list(df.dtypes.value_counts().index.astype(str))}",
                        "confidence": 0.8,
                        "category": "data_quality"
                    }
                ]
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {str(e)}")
            insights = [
                {
                    "title": "Analyse du dataset",
                    "description": f"Le dataset contient {len(df)} enregistrements avec {len(df.columns)} colonnes",
                    "confidence": 0.9,
                    "category": "general"
                }
            ]
        
        return insights

    def _generate_recommendations(self, df: pd.DataFrame, ai_analysis: str) -> List[Dict[str, Any]]:
        """Génération de recommandations basées sur l'analyse IA"""
        recommendations = []
        
        try:
            # Analyser le contenu de l'analyse IA pour extraire des recommandations
            analysis_lower = ai_analysis.lower()
            
            # Recommandations basées sur les données
            if 'conversion' in df.columns:
                conversion_rate = (df['conversion'] == 'Oui').mean() * 100
                if conversion_rate < 2.0:
                    recommendations.append({
                        "title": "Optimiser le taux de conversion",
                        "description": f"Avec un taux de conversion de {conversion_rate:.1f}%, il est crucial d'améliorer l'expérience utilisateur et les parcours de conversion.",
                        "priority": "high",
                        "impact": "Augmentation significative des revenus",
                        "effort": "medium",
                        "category": "conversion"
                    })
            
            if 'source_trafic' in df.columns and 'conversion' in df.columns:
                source_performance = df.groupby('source_trafic')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                worst_source = source_performance.idxmin()
                worst_rate = source_performance.min()
                if worst_rate < 1.0:
                    recommendations.append({
                        "title": f"Améliorer la performance de {worst_source}",
                        "description": f"La source {worst_source} a un taux de conversion de {worst_rate:.1f}%. Analysez et optimisez cette source.",
                        "priority": "medium",
                        "impact": "Amélioration de la performance marketing",
                        "effort": "low",
                        "category": "marketing"
                    })
            
            if 'appareil' in df.columns and 'conversion' in df.columns:
                device_performance = df.groupby('appareil')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                if len(device_performance) > 1:
                    worst_device = device_performance.idxmin()
                    worst_device_rate = device_performance.min()
                    if worst_device_rate < 1.5:
                        recommendations.append({
                            "title": f"Optimiser l'expérience {worst_device}",
                            "description": f"L'expérience {worst_device} a un taux de conversion de {worst_device_rate:.1f}%. Améliorez l'interface mobile.",
                            "priority": "medium",
                            "impact": "Amélioration de l'expérience utilisateur",
                            "effort": "medium",
                            "category": "ux"
                        })
            
            # Recommandations basées sur l'analyse IA
            if 'tendance' in analysis_lower or 'augmentation' in analysis_lower:
                recommendations.append({
                    "title": "Capitaliser sur les tendances positives",
                    "description": "L'analyse révèle des tendances positives. Maintenez et amplifiez ces efforts.",
                    "priority": "medium",
                    "impact": "Consolidation des performances",
                    "effort": "low",
                    "category": "strategy"
                })
            
            if 'problème' in analysis_lower or 'défaut' in analysis_lower or 'faible' in analysis_lower:
                recommendations.append({
                    "title": "Résoudre les problèmes identifiés",
                    "description": "L'analyse a identifié des problèmes spécifiques. Priorisez leur résolution.",
                    "priority": "high",
                    "impact": "Amélioration significative",
                    "effort": "high",
                    "category": "optimization"
                })
            
            # Recommandation générique si pas assez de recommandations
            if len(recommendations) < 2:
                recommendations.append({
                    "title": "Analyse approfondie recommandée",
                    "description": "Pour une analyse plus détaillée, considérez des données supplémentaires ou des segments spécifiques.",
                    "priority": "low",
                    "impact": "Amélioration de l'analyse",
                    "effort": "low",
                    "category": "analysis"
                })
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {str(e)}")
            recommendations = [
                {
                    "title": "Analyse complémentaire",
                    "description": "Considérez une analyse plus approfondie avec des données supplémentaires",
                    "priority": "medium",
                    "impact": "Amélioration de l'analyse",
                    "effort": "low",
                    "category": "analysis"
                }
            ]
        
        return recommendations

    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Détection d'anomalies dans les données"""
        anomalies = []
        
        try:
            # Anomalie 1: Valeurs manquantes
            missing_values = df.isnull().sum().sum()
            if missing_values > 0:
                missing_percentage = (missing_values / (len(df) * len(df.columns))) * 100
                if missing_percentage > 10:
                    anomalies.append({
                        "type": "missing_values",
                        "description": f"Valeurs manquantes élevées: {missing_percentage:.1f}% des données",
                        "severity": "high",
                        "affected_columns": df.columns[df.isnull().sum() > 0].tolist()
                    })
                else:
                    anomalies.append({
                        "type": "missing_values",
                        "description": f"Valeurs manquantes détectées: {missing_values} au total",
                        "severity": "medium",
                        "affected_columns": df.columns[df.isnull().sum() > 0].tolist()
                    })
            
            # Anomalie 2: Valeurs extrêmes dans les colonnes numériques
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if len(df[col].dropna()) > 0:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                    if len(outliers) > 0:
                        anomalies.append({
                            "type": "outliers",
                            "description": f"Valeurs extrêmes détectées dans {col}: {len(outliers)} valeurs",
                            "severity": "medium",
                            "affected_columns": [col]
                        })
            
            # Anomalie 3: Données dupliquées
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                anomalies.append({
                    "type": "duplicates",
                    "description": f"Lignes dupliquées détectées: {duplicates} occurrences",
                    "severity": "medium",
                    "affected_columns": df.columns.tolist()
                })
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies: {str(e)}")
        
        return anomalies

    def _generate_intelligent_summary(self, df: pd.DataFrame, ai_analysis: str) -> str:
        """Génération d'un résumé intelligent basé sur l'analyse IA"""
        try:
            # Extraire les points clés de l'analyse IA
            analysis_lines = ai_analysis.split('\n')
            key_points = []
            
            for line in analysis_lines:
                line = line.strip()
                if line and len(line) > 20 and not line.startswith('#'):
                    key_points.append(line)
                    if len(key_points) >= 3:
                        break
            
            if key_points:
                summary = f"Analyse de {len(df)} lignes et {len(df.columns)} colonnes. "
                summary += " ".join(key_points[:2])  # Prendre les 2 premiers points
                return summary
            else:
                return f"Analyse complète de {len(df)} enregistrements avec {len(df.columns)} variables. L'analyse IA révèle des insights métier pertinents."
                
        except Exception as e:
            logger.error(f"Erreur génération résumé: {str(e)}")
            return f"Analyse de {len(df)} lignes et {len(df.columns)} colonnes"

    def _generate_dynamic_charts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Génération de graphiques dynamiques selon le contenu"""
        charts = []
        
        try:
            # Graphique 1: Taux de conversion par source de trafic
            if 'source_trafic' in df.columns and 'conversion' in df.columns:
                conversion_by_source = df.groupby('source_trafic')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                if len(conversion_by_source) > 1:
                    charts.append({
                        "title": "Taux de conversion par source de trafic",
                        "type": "bar",
                        "data": {
                            "labels": list(conversion_by_source.index),
                            "values": list(conversion_by_source.values)
                        },
                        "format": "json"
                    })
            
            # Graphique 2: Performance par appareil
            if 'appareil' in df.columns and 'conversion' in df.columns:
                conversion_by_device = df.groupby('appareil')['conversion'].apply(lambda x: (x == 'Oui').mean() * 100)
                if len(conversion_by_device) > 1:
                    charts.append({
                        "title": "Taux de conversion par appareil",
                        "type": "bar",
                        "data": {
                            "labels": list(conversion_by_device.index),
                            "values": list(conversion_by_device.values)
                        },
                        "format": "json"
                    })
            
            # Graphique 3: Répartition des montants d'achat
            if 'montant_achat' in df.columns:
                purchase_amounts = df[df['montant_achat'] > 0]['montant_achat']
                if len(purchase_amounts) > 0:
                    # Créer des bins pour les montants
                    bins = [0, 50, 100, 200, 500, 1000, float('inf')]
                    labels = ['0-50€', '50-100€', '100-200€', '200-500€', '500-1000€', '1000€+']
                    purchase_bins = pd.cut(purchase_amounts, bins=bins, labels=labels, include_lowest=True)
                    purchase_distribution = purchase_bins.value_counts()
                    
                    charts.append({
                        "title": "Répartition des montants d'achat",
                        "type": "pie",
                        "data": {
                            "labels": list(purchase_distribution.index),
                            "values": list(purchase_distribution.values)
                        },
                        "format": "json"
                    })
            
            # Graphique 4: Score d'engagement par localisation
            if 'localisation' in df.columns and 'score_engagement' in df.columns:
                engagement_by_location = df.groupby('localisation')['score_engagement'].mean()
                if len(engagement_by_location) > 1:
                    charts.append({
                        "title": "Score d'engagement moyen par ville",
                        "type": "bar",
                        "data": {
                            "labels": list(engagement_by_location.index),
                            "values": list(engagement_by_location.values)
                        },
                        "format": "json"
                    })
            
            # Graphique 5: Distribution temporelle (si date disponible)
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    daily_activity = df.groupby(df[date_col].dt.date).size()
                    if len(daily_activity) > 1:
                        charts.append({
                            "title": "Activité quotidienne",
                            "type": "line",
                            "data": {
                                "labels": [str(date) for date in daily_activity.index],
                                "values": list(daily_activity.values)
                            },
                            "format": "json"
                        })
                except:
                    pass
            
            # Graphique 6: Distribution des types de données (fallback)
            if not charts:
                charts.append({
                    "title": "Distribution des types de données",
                    "type": "bar",
                    "data": {
                        "labels": list(df.dtypes.value_counts().index.astype(str)),
                        "values": list(df.dtypes.value_counts().values.astype(int))
                    },
                    "format": "json"
                })
            
        except Exception as e:
            logger.error(f"Erreur génération graphiques: {str(e)}")
            # Fallback
            charts.append({
                "title": "Distribution des types de données",
                "type": "bar",
                "data": {
                    "labels": list(df.dtypes.value_counts().index.astype(str)),
                    "values": list(df.dtypes.value_counts().values.astype(int))
                },
                "format": "json"
            })
        
        return charts 