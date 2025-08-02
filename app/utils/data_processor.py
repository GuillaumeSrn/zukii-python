import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

def convert_numpy_types(obj):
    """Convertit les types numpy en types Python natifs pour la sérialisation JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.datetime64):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

class DataProcessor:
    """Processeur de données CSV pour l'analyse IA"""
    
    @staticmethod
    def load_csv_from_bytes(content: bytes) -> pd.DataFrame:
        """Charge un DataFrame depuis des bytes CSV"""
        try:
            # Essayer différents encodages
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        pd.io.common.BytesIO(content),
                        encoding=encoding,
                        na_values=['', 'nan', 'NaN', 'NULL', 'null'],
                        keep_default_na=True
                    )
                    return df
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Impossible de décoder le fichier CSV")
            
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement CSV: {str(e)}")
    
    @staticmethod
    def load_csv_data(csv_content: str) -> pd.DataFrame:
        """Charge un DataFrame depuis une chaîne CSV"""
        try:
            df = pd.read_csv(
                pd.io.common.StringIO(csv_content),
                na_values=['', 'nan', 'NaN', 'NULL', 'null'],
                keep_default_na=True
            )
            return df
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement CSV: {str(e)}")

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et prépare un DataFrame pour l'analyse"""
        df_clean = df.copy()
        
        # Supprimer les lignes complètement vides
        df_clean = df_clean.dropna(how='all')
        
        # Nettoyer les noms de colonnes
        df_clean.columns = [str(col).strip().lower().replace(' ', '_') for col in df_clean.columns]
        
        # Convertir les colonnes de dates
        df_clean = DataProcessor._convert_date_columns(df_clean)
        
        # Nettoyer les valeurs numériques
        df_clean = DataProcessor._clean_numeric_columns(df_clean)
        
        return df_clean

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données en supprimant les lignes avec valeurs manquantes"""
        df_clean = df.copy()
        # Supprimer les lignes avec des valeurs manquantes
        df_clean = df_clean.dropna()
        return df_clean

    @staticmethod
    def _convert_date_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convertit les colonnes de dates"""
        date_patterns = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
            '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d %H:%M:%S'
        ]
        
        for col in df.columns:
            try:
                # Vérification de sécurité pour l'attribut dtype
                if hasattr(df[col], 'dtype') and str(df[col].dtype) == 'object':
                    # Essayer de détecter si c'est une colonne de date
                    sample_values = df[col].dropna().head(10)
                    
                    for pattern in date_patterns:
                        try:
                            pd.to_datetime(sample_values, format=pattern)
                            df[col] = pd.to_datetime(df[col], format=pattern, errors='coerce')
                            break
                        except:
                            continue
            except Exception:
                # En cas d'erreur, on continue avec la colonne suivante
                continue
        
        return df
    
    @staticmethod
    def _clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les colonnes numériques"""
        for col in df.columns:
            try:
                # Vérification de sécurité pour l'attribut dtype
                if hasattr(df[col], 'dtype') and str(df[col].dtype) == 'object':
                    # Essayer de convertir en numérique
                    try:
                        # Nettoyer les caractères non numériques
                        cleaned = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                        numeric_values = pd.to_numeric(cleaned, errors='coerce')
                        
                        # Si plus de 50% des valeurs sont numériques, convertir
                        if numeric_values.notna().sum() / len(numeric_values) > 0.5:
                            df[col] = numeric_values
                    except:
                        continue
            except Exception:
                # En cas d'erreur, on continue avec la colonne suivante
                continue
        
        return df
    
    @staticmethod
    def generate_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Génère un résumé des données pour l'analyse IA"""
        summary = {
            "shape": {
                "rows": len(df),
                "columns": len(df.columns)
            },
            "columns": {},
            "data_types": {},
            "missing_values": {},
            "basic_stats": {},
            "sample_data": {}
        }
        
        # Informations sur les colonnes
        for col in df.columns:
            try:
                # Vérification de sécurité pour l'attribut dtype
                if not hasattr(df[col], 'dtype'):
                    # Si la colonne n'a pas d'attribut dtype, on la traite comme object
                    col_dtype = 'object'
                else:
                    col_dtype = str(df[col].dtype)
                
                col_info = {
                    "name": str(col),
                    "dtype": col_dtype,
                    "missing_count": int(df[col].isna().sum()),
                    "missing_percentage": float((df[col].isna().sum() / len(df)) * 100),
                    "unique_count": int(df[col].nunique())
                }
                
                summary["columns"][str(col)] = col_info
                summary["data_types"][str(col)] = col_dtype
                summary["missing_values"][str(col)] = int(df[col].isna().sum())
                
                # Statistiques de base selon le type
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats = {
                        "min": float(df[col].min()) if not df[col].isna().all() else None,
                        "max": float(df[col].max()) if not df[col].isna().all() else None,
                        "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                        "median": float(df[col].median()) if not df[col].isna().all() else None,
                        "std": float(df[col].std()) if not df[col].isna().all() else None
                    }
                    summary["basic_stats"][str(col)] = col_stats
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_stats = {
                        "min": df[col].min().isoformat() if not df[col].isna().all() else None,
                        "max": df[col].max().isoformat() if not df[col].isna().all() else None,
                        "range_days": int((df[col].max() - df[col].min()).days) if not df[col].isna().all() else None
                    }
                    summary["basic_stats"][str(col)] = col_stats
                else:
                    # Colonnes catégorielles
                    value_counts = df[col].value_counts().head(10)
                    value_counts_dict = {str(k): int(v) for k, v in value_counts.items()}
                    col_stats = {
                        "top_values": value_counts_dict,
                        "most_common": str(df[col].mode().iloc[0]) if not df[col].mode().empty else None
                    }
                    summary["basic_stats"][str(col)] = col_stats
                
                # Échantillon de données
                sample_values = df[col].dropna().head(5).tolist()
                # Convertir en types JSON-sérialisables
                serializable_samples = []
                for val in sample_values:
                    if pd.isna(val):
                        serializable_samples.append(None)
                    elif isinstance(val, (np.integer, np.floating)):
                        serializable_samples.append(float(val))
                    elif isinstance(val, np.datetime64):
                        serializable_samples.append(val.isoformat())
                    else:
                        serializable_samples.append(str(val))
                summary["sample_data"][str(col)] = serializable_samples
            except Exception as e:
                # En cas d'erreur, on continue avec la colonne suivante
                continue
        
        # Statistiques globales
        summary["global_stats"] = {
            "total_missing_values": int(df.isna().sum().sum()),
            "missing_percentage": float((df.isna().sum().sum() / (len(df) * len(df.columns))) * 100),
            "numeric_columns": int(len(df.select_dtypes(include=[np.number]).columns)),
            "categorical_columns": int(len(df.select_dtypes(include=['object']).columns)),
            "datetime_columns": int(len(df.select_dtypes(include=['datetime']).columns))
        }
        
        # Convertir tous les types numpy en types Python natifs
        return convert_numpy_types(summary)

    @staticmethod
    def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Génère un résumé simple des données"""
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_types": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {str(col): int(count) for col, count in df.isnull().sum().items()}
        }
        return summary

    @staticmethod
    def detect_anomalies_general(df: pd.DataFrame) -> Dict[str, Any]:
        """Détecte les anomalies dans les données"""
        anomalies = {
            "outliers": {},
            "missing_patterns": {},
            "data_quality_issues": []
        }
        
        # Détection d'outliers pour les colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_str = str(col)
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            if len(outliers) > 0:
                anomalies["outliers"][col_str] = {
                    "count": int(len(outliers)),
                    "percentage": float((len(outliers) / len(df)) * 100),
                    "indices": [int(idx) for idx in outliers.index.tolist()]
                }
        
        # Patterns de valeurs manquantes
        missing_data = df.isnull()
        missing_patterns = missing_data.groupby(missing_data.columns.tolist()).size()
        
        if len(missing_patterns) > 1:
            # Convertir les patterns en format JSON-sérialisable
            patterns_dict = {}
            for pattern, count in missing_patterns.items():
                # Convertir le tuple de pattern en liste de booléens
                pattern_list = [bool(val) for val in pattern]
                patterns_dict[str(pattern_list)] = int(count)
            
            anomalies["missing_patterns"] = {
                "unique_patterns": int(len(missing_patterns)),
                "patterns": patterns_dict
            }
        
        # Problèmes de qualité des données
        for col in df.columns:
            col_str = str(col)
            # Colonnes avec trop de valeurs manquantes
            if df[col].isna().sum() / len(df) > 0.5:
                anomalies["data_quality_issues"].append({
                    "type": "high_missing_values",
                    "column": col_str,
                    "missing_percentage": float((df[col].isna().sum() / len(df)) * 100)
                })
            
            # Colonnes avec trop de valeurs uniques (potentiellement des IDs)
            if df[col].nunique() / len(df) > 0.9:
                anomalies["data_quality_issues"].append({
                    "type": "high_cardinality",
                    "column": col_str,
                    "unique_percentage": float((df[col].nunique() / len(df)) * 100)
                })
        
        return anomalies

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, column: str) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans une colonne spécifique"""
        anomalies = []
        
        if column not in df.columns:
            return anomalies
            
        col_data = df[column].dropna()
        
        if col_data.dtype in ['int64', 'float64']:
            # Détection d'outliers avec méthode IQR
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            
            for outlier in outliers:
                anomalies.append({
                    "type": "outlier",
                    "value": float(outlier),
                    "column": str(column),
                    "description": f"Valeur aberrante détectée: {outlier}"
                })
        
        return anomalies

    @staticmethod
    def prepare_data_for_analysis(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Prépare les données pour l'analyse IA"""
        # Nettoyer les données
        df_clean = DataProcessor.clean_dataframe(df)
        
        # Générer le résumé
        summary = DataProcessor.generate_data_summary(df_clean)
        
        # Détecter les anomalies
        anomalies = DataProcessor.detect_anomalies_general(df_clean)
        summary["anomalies"] = anomalies
        
        return df_clean, summary 