import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from app.utils.logger import get_logger

class VisualizationService:
    """Service de génération de graphiques Plotly"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Configuration par défaut des graphiques
        self.default_config = {
            "displayModeBar": True,
            "responsive": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"]
        }
        
        # Couleurs par défaut
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def generate_chart(
        self, 
        data: pd.DataFrame, 
        chart_config: Dict[str, Any],
        analysis_id: str = None
    ) -> Dict[str, Any]:
        """Génère un graphique Plotly selon la configuration"""
        
        start_time = datetime.now()
        
        try:
            chart_type = chart_config.get("type", "line")
            
            if chart_type == "line":
                chart_data = self._create_line_chart(data, chart_config)
            elif chart_type == "bar":
                chart_data = self._create_bar_chart(data, chart_config)
            elif chart_type == "scatter":
                chart_data = self._create_scatter_chart(data, chart_config)
            elif chart_type == "heatmap":
                chart_data = self._create_heatmap(data, chart_config)
            elif chart_type == "histogram":
                chart_data = self._create_histogram(data, chart_config)
            elif chart_type == "box":
                chart_data = self._create_box_chart(data, chart_config)
            elif chart_type == "pie":
                chart_data = self._create_pie_chart(data, chart_config)
            else:
                chart_data = self._create_default_chart(data, chart_config)
            
            # Ajouter les métadonnées
            chart_data["generation_time"] = (datetime.now() - start_time).total_seconds()
            chart_data["data_points"] = len(data)
            
            # Log de la génération
            if analysis_id:
                self.logger.log_performance(
                    operation=f"chart_generation_{chart_type}",
                    duration=chart_data["generation_time"],
                    analysis_id=analysis_id
                )
            
            return chart_data
            
        except Exception as e:
            self.logger.log_error(
                error_type="chart_generation_error",
                message=f"Erreur lors de la génération du graphique {chart_config.get('type', 'unknown')}: {str(e)}",
                analysis_id=analysis_id
            )
            return self._create_error_chart(str(e))
    
    def _create_line_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique en ligne"""
        x_col = config.get("x_column", self._detect_best_x_column(data))
        y_col = config.get("y_column", self._detect_best_y_column(data))
        
        # Vérifier que les colonnes existent
        if x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Colonnes {x_col} ou {y_col} non trouvées dans les données")
        
        # Trier par x si c'est une date
        if pd.api.types.is_datetime64_any_dtype(data[x_col]):
            data = data.sort_values(x_col)
        
        fig = px.line(
            data, 
            x=x_col, 
            y=y_col,
            title=config.get("title", f"Évolution de {y_col}"),
            labels={x_col: config.get("x_label", x_col), y_col: config.get("y_label", y_col)},
            color=config.get("color_column"),
            line_group=config.get("line_group"),
            hover_data=config.get("hover_data", [])
        )
        
        # Personnalisation
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "line",
            "title": config.get("title", f"Évolution de {y_col}"),
            "description": config.get("description", f"Graphique en ligne montrant l'évolution de {y_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_bar_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique en barres"""
        x_col = config.get("x_column", self._detect_best_x_column(data))
        y_col = config.get("y_column", self._detect_best_y_column(data))
        
        if x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Colonnes {x_col} ou {y_col} non trouvées dans les données")
        
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=config.get("title", f"Comparaison de {y_col}"),
            labels={x_col: config.get("x_label", x_col), y_col: config.get("y_label", y_col)},
            color=config.get("color_column"),
            barmode=config.get("barmode", "group"),
            orientation=config.get("orientation", "v")
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "bar",
            "title": config.get("title", f"Comparaison de {y_col}"),
            "description": config.get("description", f"Graphique en barres comparant {y_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_scatter_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique de dispersion"""
        x_col = config.get("x_column", self._detect_best_x_column(data))
        y_col = config.get("y_column", self._detect_best_y_column(data))
        
        if x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Colonnes {x_col} ou {y_col} non trouvées dans les données")
        
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            title=config.get("title", f"Corrélation entre {x_col} et {y_col}"),
            labels={x_col: config.get("x_label", x_col), y_col: config.get("y_label", y_col)},
            color=config.get("color_column"),
            size=config.get("size_column"),
            hover_data=config.get("hover_data", [])
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "scatter",
            "title": config.get("title", f"Corrélation entre {x_col} et {y_col}"),
            "description": config.get("description", f"Nuage de points montrant la relation entre {x_col} et {y_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_heatmap(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une heatmap de corrélations"""
        # Calculer la matrice de corrélation
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) < 2:
            raise ValueError("Pas assez de colonnes numériques pour créer une heatmap")
        
        corr_matrix = numeric_data.corr()
        
        fig = px.imshow(
            corr_matrix,
            title=config.get("title", "Matrice de corrélation"),
            labels=dict(x="Variables", y="Variables", color="Corrélation"),
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 500),
            width=config.get("width", 600)
        )
        
        return {
            "type": "heatmap",
            "title": config.get("title", "Matrice de corrélation"),
            "description": config.get("description", "Heatmap des corrélations entre variables numériques"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 500)
        }
    
    def _create_histogram(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un histogramme"""
        x_col = config.get("x_column", self._detect_best_y_column(data))
        
        if x_col not in data.columns:
            raise ValueError(f"Colonne {x_col} non trouvée dans les données")
        
        fig = px.histogram(
            data,
            x=x_col,
            title=config.get("title", f"Distribution de {x_col}"),
            labels={x_col: config.get("x_label", x_col)},
            nbins=config.get("nbins", 30),
            color=config.get("color_column")
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "histogram",
            "title": config.get("title", f"Distribution de {x_col}"),
            "description": config.get("description", f"Histogramme de la distribution de {x_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_box_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique en boîte"""
        x_col = config.get("x_column", self._detect_best_x_column(data))
        y_col = config.get("y_column", self._detect_best_y_column(data))
        
        if y_col not in data.columns:
            raise ValueError(f"Colonne {y_col} non trouvée dans les données")
        
        fig = px.box(
            data,
            x=x_col if x_col in data.columns else None,
            y=y_col,
            title=config.get("title", f"Distribution de {y_col}"),
            labels={x_col: config.get("x_label", x_col), y_col: config.get("y_label", y_col)},
            color=config.get("color_column")
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "box",
            "title": config.get("title", f"Distribution de {y_col}"),
            "description": config.get("description", f"Graphique en boîte de la distribution de {y_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_pie_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique circulaire"""
        names_col = config.get("names_column", self._detect_best_x_column(data))
        values_col = config.get("values_column", self._detect_best_y_column(data))
        
        if names_col not in data.columns or values_col not in data.columns:
            raise ValueError(f"Colonnes {names_col} ou {values_col} non trouvées dans les données")
        
        fig = px.pie(
            data,
            names=names_col,
            values=values_col,
            title=config.get("title", f"Répartition de {values_col}"),
            hole=config.get("hole", 0)
        )
        
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            height=config.get("height", 400),
            width=config.get("width", 600)
        )
        
        return {
            "type": "pie",
            "title": config.get("title", f"Répartition de {values_col}"),
            "description": config.get("description", f"Graphique circulaire de la répartition de {values_col}"),
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": config.get("width", 600),
            "height": config.get("height", 400)
        }
    
    def _create_default_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un graphique par défaut (ligne)"""
        return self._create_line_chart(data, config)
    
    def _create_error_chart(self, error_message: str) -> Dict[str, Any]:
        """Crée un graphique d'erreur"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"Erreur de génération: {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        
        fig.update_layout(
            template="plotly_white",
            title="Erreur de génération de graphique",
            height=400,
            width=600
        )
        
        return {
            "type": "error",
            "title": "Erreur de génération",
            "description": f"Impossible de générer le graphique: {error_message}",
            "data": json.loads(fig.to_json()),
            "config": self.default_config,
            "width": 600,
            "height": 400,
            "error": True
        }
    
    def generate_dashboard(self, data: pd.DataFrame, analysis_result: Dict[str, Any], analysis_id: str = None) -> Dict[str, Any]:
        """Génère un dashboard complet avec plusieurs graphiques"""
        start_time = datetime.now()
        
        dashboard = {
            "title": analysis_result.get("summary", "Dashboard d'analyse"),
            "charts": [],
            "summary": analysis_result.get("key_insights", []),
            "generation_time": 0.0
        }
        
        try:
            # Génération automatique de graphiques basés sur les suggestions
            suggested_charts = analysis_result.get("suggested_charts", [])
            
            for i, chart_suggestion in enumerate(suggested_charts[:4]):  # Max 4 graphiques
                try:
                    chart_config = {
                        "type": chart_suggestion.get("type", "line"),
                        "title": chart_suggestion.get("title", f"Graphique {i+1}"),
                        "description": chart_suggestion.get("description", ""),
                        "x_column": self._detect_best_x_column(data),
                        "y_column": self._detect_best_y_column(data),
                        "color_column": self._detect_best_color_column(data),
                        "width": 600,
                        "height": 400
                    }
                    
                    # Mettre à jour avec les suggestions spécifiques
                    if "x_column" in chart_suggestion:
                        chart_config["x_column"] = chart_suggestion["x_column"]
                    if "y_column" in chart_suggestion:
                        chart_config["y_column"] = chart_suggestion["y_column"]
                    if "color_column" in chart_suggestion:
                        chart_config["color_column"] = chart_suggestion["color_column"]
                    
                    chart = self.generate_chart(data, chart_config, analysis_id)
                    
                    if not chart.get("error", False):
                        dashboard["charts"].append(chart)
                        
                except Exception as e:
                    self.logger.log_error(
                        error_type="dashboard_chart_error",
                        message=f"Erreur lors de la génération du graphique {i+1}: {str(e)}",
                        analysis_id=analysis_id
                    )
                    continue
            
            # Si aucun graphique n'a été généré, créer un graphique par défaut
            if not dashboard["charts"]:
                default_chart = self.generate_chart(
                    data, 
                    {"type": "line", "title": "Vue d'ensemble des données"},
                    analysis_id
                )
                dashboard["charts"].append(default_chart)
            
            dashboard["generation_time"] = (datetime.now() - start_time).total_seconds()
            
            return dashboard
            
        except Exception as e:
            self.logger.log_error(
                error_type="dashboard_generation_error",
                message=f"Erreur lors de la génération du dashboard: {str(e)}",
                analysis_id=analysis_id
            )
            return {
                "title": "Erreur de génération du dashboard",
                "charts": [self._create_error_chart(str(e))],
                "summary": [],
                "generation_time": (datetime.now() - start_time).total_seconds(),
                "error": True
            }
    
    def _detect_best_x_column(self, data: pd.DataFrame) -> str:
        """Détecte la meilleure colonne pour l'axe X"""
        # Priorité: date, catégorie, puis première colonne
        for col in data.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                return col
            if data[col].dtype == 'object' and len(data[col].unique()) < 20:
                return col
        return data.columns[0] if len(data.columns) > 0 else "index"
    
    def _detect_best_y_column(self, data: pd.DataFrame) -> str:
        """Détecte la meilleure colonne pour l'axe Y"""
        # Priorité: colonnes numériques
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            return numeric_cols[0]
        return data.columns[1] if len(data.columns) > 1 else data.columns[0]
    
    def _detect_best_color_column(self, data: pd.DataFrame) -> Optional[str]:
        """Détecte la meilleure colonne pour la couleur"""
        # Colonnes catégorielles avec peu de valeurs uniques
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if 2 <= len(data[col].unique()) <= 10:
                return col
        
        return None 