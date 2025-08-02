import pandas as pd
import hashlib
import re
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.utils.logger import get_logger

class AnonymizationService:
    """Service de protection des données RGPD"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Patterns pour détecter les données sensibles
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_fr': r'(\+33|0)[1-9](\d{8})',
            'phone_intl': r'\+[1-9]\d{1,14}',
            'ssn_fr': r'\b\d{15}\b',  # Numéro de sécurité sociale français
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
            'postal_code_fr': r'\b\d{5}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'mac_address': r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'
        }
        
        # Colonnes sensibles par défaut
        self.sensitive_column_keywords = [
            'email', 'mail', 'phone', 'téléphone', 'tel', 'mobile',
            'ssn', 'social', 'security', 'numéro', 'number',
            'credit', 'card', 'carte', 'iban', 'account', 'compte',
            'address', 'adresse', 'postal', 'zip', 'code',
            'ip', 'mac', 'id', 'identifier', 'identifiant',
            'password', 'mot_de_passe', 'secret', 'token'
        ]
    
    def anonymize_dataframe(self, df: pd.DataFrame, analysis_id: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Anonymise un DataFrame en préservant la structure
        
        Returns:
            Tuple[pd.DataFrame, Dict]: (DataFrame anonymisé, rapport d'anonymisation)
        """
        start_time = datetime.now()
        df_anon = df.copy()
        anonymization_report = {
            "columns_processed": 0,
            "columns_anonymized": 0,
            "sensitive_columns_detected": [],
            "anonymization_methods": {},
            "data_loss_estimate": 0.0,
            "processing_time": 0.0
        }
        
        try:
            for column in df_anon.columns:
                anonymization_report["columns_processed"] += 1
                
                if self._contains_sensitive_data(df_anon[column], column):
                    anonymization_report["sensitive_columns_detected"].append(column)
                    anonymization_report["columns_anonymized"] += 1
                    
                    # Anonymiser la colonne
                    original_values = df_anon[column].copy()
                    df_anon[column] = self._anonymize_column(df_anon[column], column)
                    
                    # Calculer la perte de données
                    data_loss = self._calculate_data_loss(original_values, df_anon[column])
                    anonymization_report["data_loss_estimate"] += data_loss
                    
                    # Enregistrer la méthode utilisée
                    anonymization_report["anonymization_methods"][column] = {
                        "method": self._get_anonymization_method(column),
                        "data_loss": data_loss
                    }
            
            anonymization_report["processing_time"] = (datetime.now() - start_time).total_seconds()
            
            # Log de l'anonymisation
            if analysis_id:
                self.logger.log_privacy_event(
                    analysis_id=analysis_id,
                    event_type="anonymization_completed",
                    details=anonymization_report
                )
            
            return df_anon, anonymization_report
            
        except Exception as e:
            self.logger.log_error(
                error_type="anonymization_error",
                message=f"Erreur lors de l'anonymisation: {str(e)}",
                analysis_id=analysis_id
            )
            raise
    
    def _contains_sensitive_data(self, series: pd.Series, column_name: str) -> bool:
        """Détecte si une colonne contient des données sensibles"""
        # Vérifier le nom de la colonne
        column_lower = column_name.lower()
        for keyword in self.sensitive_column_keywords:
            if keyword in column_lower:
                return True
        
        # Vérifier le contenu avec les patterns
        sample_data = series.dropna().head(100).astype(str)
        
        for pattern_name, pattern in self.patterns.items():
            # Échapper les caractères spéciaux pour éviter les warnings regex
            escaped_pattern = re.escape(pattern)
            if sample_data.str.contains(escaped_pattern, regex=True, na=False).any():
                return True
        
        # Vérifier la cardinalité (trop de valeurs uniques = potentiellement des IDs)
        if series.nunique() / len(series) > 0.9:
            return True
        
        return False
    
    def _anonymize_column(self, series: pd.Series, column_name: str) -> pd.Series:
        """Anonymise une colonne avec la méthode appropriée"""
        column_lower = column_name.lower()
        
        # Méthodes d'anonymisation selon le type de données
        if any(keyword in column_lower for keyword in ['email', 'mail']):
            return self._anonymize_emails(series)
        elif any(keyword in column_lower for keyword in ['phone', 'téléphone', 'tel', 'mobile']):
            return self._anonymize_phones(series)
        elif any(keyword in column_lower for keyword in ['ssn', 'social', 'security']):
            return self._anonymize_ssn(series)
        elif any(keyword in column_lower for keyword in ['credit', 'card', 'carte', 'iban']):
            return self._anonymize_financial(series)
        elif any(keyword in column_lower for keyword in ['address', 'adresse', 'postal', 'zip']):
            return self._anonymize_addresses(series)
        elif any(keyword in column_lower for keyword in ['ip', 'mac']):
            return self._anonymize_network(series)
        elif any(keyword in column_lower for keyword in ['id', 'identifier', 'identifiant']):
            return self._anonymize_ids(series)
        else:
            # Anonymisation générique par hash
            return self._anonymize_generic(series)
    
    def _anonymize_emails(self, series: pd.Series) -> pd.Series:
        """Anonymise les adresses email"""
        def anonymize_email(email):
            if pd.isna(email):
                return email
            
            email_str = str(email)
            if '@' in email_str:
                username, domain = email_str.split('@', 1)
                # Garder le premier et dernier caractère du username
                if len(username) > 2:
                    anonymized_username = username[0] + '*' * (len(username) - 2) + username[-1]
                else:
                    anonymized_username = '*' * len(username)
                
                # Anonymiser le domaine
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    anonymized_domain = '*' * len(domain_parts[0]) + '.' + '.'.join(domain_parts[1:])
                else:
                    anonymized_domain = '*' * len(domain)
                
                return f"{anonymized_username}@{anonymized_domain}"
            else:
                return self._hash_value(email_str)
        
        return series.apply(anonymize_email)
    
    def _anonymize_phones(self, series: pd.Series) -> pd.Series:
        """Anonymise les numéros de téléphone"""
        def anonymize_phone(phone):
            if pd.isna(phone):
                return phone
            
            phone_str = str(phone)
            # Garder les 2 premiers et 2 derniers chiffres
            digits_only = re.sub(r'\D', '', phone_str)
            if len(digits_only) >= 4:
                return digits_only[:2] + '*' * (len(digits_only) - 4) + digits_only[-2:]
            else:
                return '*' * len(digits_only)
        
        return series.apply(anonymize_phone)
    
    def _anonymize_ssn(self, series: pd.Series) -> pd.Series:
        """Anonymise les numéros de sécurité sociale"""
        def anonymize_ssn(ssn):
            if pd.isna(ssn):
                return ssn
            
            ssn_str = str(ssn)
            digits_only = re.sub(r'\D', '', ssn_str)
            if len(digits_only) >= 6:
                return digits_only[:3] + '*' * (len(digits_only) - 6) + digits_only[-3:]
            else:
                return '*' * len(digits_only)
        
        return series.apply(anonymize_ssn)
    
    def _anonymize_financial(self, series: pd.Series) -> pd.Series:
        """Anonymise les données financières"""
        def anonymize_financial(data):
            if pd.isna(data):
                return data
            
            data_str = str(data)
            digits_only = re.sub(r'\D', '', data_str)
            if len(digits_only) >= 8:
                return digits_only[:4] + '*' * (len(digits_only) - 8) + digits_only[-4:]
            else:
                return '*' * len(digits_only)
        
        return series.apply(anonymize_financial)
    
    def _anonymize_addresses(self, series: pd.Series) -> pd.Series:
        """Anonymise les adresses"""
        def anonymize_address(address):
            if pd.isna(address):
                return address
            
            address_str = str(address)
            # Garder seulement le code postal et la ville
            parts = address_str.split(',')
            if len(parts) >= 2:
                return f"***, {parts[-1].strip()}"
            else:
                return self._hash_value(address_str)
        
        return series.apply(anonymize_address)
    
    def _anonymize_network(self, series: pd.Series) -> pd.Series:
        """Anonymise les adresses réseau"""
        def anonymize_network(network):
            if pd.isna(network):
                return network
            
            network_str = str(network)
            if '.' in network_str:  # IP address
                parts = network_str.split('.')
                if len(parts) == 4:
                    return f"{parts[0]}.{parts[1]}.*.*"
            elif ':' in network_str:  # MAC address
                parts = network_str.split(':')
                if len(parts) == 6:
                    return f"{parts[0]}:{parts[1]}:*:*:*:*"
            
            return self._hash_value(network_str)
        
        return series.apply(anonymize_network)
    
    def _anonymize_ids(self, series: pd.Series) -> pd.Series:
        """Anonymise les identifiants"""
        # Mapping pour maintenir la cohérence des IDs
        id_mapping = {}
        
        def anonymize_id(id_val):
            if pd.isna(id_val):
                return id_val
            
            id_str = str(id_val)
            if id_str not in id_mapping:
                id_mapping[id_str] = f"ID_{len(id_mapping) + 1:06d}"
            
            return id_mapping[id_str]
        
        return series.apply(anonymize_id)
    
    def _anonymize_generic(self, series: pd.Series) -> pd.Series:
        """Anonymisation générique par hash"""
        return series.apply(lambda x: self._hash_value(x) if pd.notna(x) else x)
    
    def _hash_value(self, value: Any) -> str:
        """Hash sécurisé avec sel pour anonymisation"""
        salt = "zukii_anon_2024"
        return hashlib.sha256(f"{salt}{str(value)}".encode()).hexdigest()[:8]
    
    def _get_anonymization_method(self, column_name: str) -> str:
        """Retourne la méthode d'anonymisation utilisée"""
        column_lower = column_name.lower()
        
        if any(keyword in column_lower for keyword in ['email', 'mail']):
            return "email_masking"
        elif any(keyword in column_lower for keyword in ['phone', 'téléphone', 'tel', 'mobile']):
            return "phone_masking"
        elif any(keyword in column_lower for keyword in ['ssn', 'social', 'security']):
            return "ssn_masking"
        elif any(keyword in column_lower for keyword in ['credit', 'card', 'carte', 'iban']):
            return "financial_masking"
        elif any(keyword in column_lower for keyword in ['address', 'adresse', 'postal', 'zip']):
            return "address_masking"
        elif any(keyword in column_lower for keyword in ['ip', 'mac']):
            return "network_masking"
        elif any(keyword in column_lower for keyword in ['id', 'identifier', 'identifiant']):
            return "id_mapping"
        else:
            return "hash_anonymization"
    
    def _calculate_data_loss(self, original: pd.Series, anonymized: pd.Series) -> float:
        """Calcule l'estimation de perte de données"""
        if len(original) == 0:
            return 0.0
        
        # Calculer la différence de cardinalité
        original_unique = original.nunique()
        anonymized_unique = anonymized.nunique()
        
        if original_unique == 0:
            return 0.0
        
        # Perte basée sur la réduction de cardinalité
        cardinality_loss = 1 - (anonymized_unique / original_unique)
        
        # Perte basée sur la longueur moyenne des valeurs
        original_avg_length = original.astype(str).str.len().mean()
        anonymized_avg_length = anonymized.astype(str).str.len().mean()
        
        if original_avg_length == 0:
            length_loss = 0.0
        else:
            length_loss = 1 - (anonymized_avg_length / original_avg_length)
        
        # Moyenne pondérée
        return (cardinality_loss * 0.7) + (length_loss * 0.3)
    
    def generate_privacy_report(self, df: pd.DataFrame, anonymization_report: Dict[str, Any] = None) -> Dict[str, Any]:
        """Génère un rapport de confidentialité complet"""
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "sensitive_columns": self._identify_sensitive_columns(df),
            "anonymization_applied": anonymization_report is not None,
            "data_retention_days": 30,
            "compliance_status": "compliant",
            "data_processing_purpose": "analyse_ia",
            "data_controller": "Zukii",
            "anonymization_details": anonymization_report or {}
        }
        
        if anonymization_report:
            report["anonymization_details"] = anonymization_report
        
        return report
    
    def _identify_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """Identifie toutes les colonnes sensibles"""
        sensitive_columns = []
        
        for column in df.columns:
            if self._contains_sensitive_data(df[column], column):
                sensitive_columns.append(column)
        
        return sensitive_columns 