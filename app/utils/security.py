import os
import hashlib
import magic
from typing import List, Tuple
from fastapi import HTTPException, UploadFile
from app.config import settings

class SecurityValidator:
    """Validateur de sécurité pour les fichiers uploadés"""
    
    # Types MIME autorisés
    ALLOWED_MIME_TYPES = [
        'text/csv',
        'application/csv',
        'text/plain'
    ]
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = ['.csv', '.txt']
    
    # Taille maximale en bytes
    MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024
    
    @classmethod
    async def validate_file(cls, file: UploadFile) -> Tuple[bool, str]:
        """
        Valide un fichier uploadé selon les critères de sécurité
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Vérification de la taille
            if file.size and file.size > cls.MAX_FILE_SIZE:
                return False, f"Fichier trop volumineux. Taille max: {settings.max_file_size_mb}MB"
            
            # Vérification de l'extension
            if not cls._is_valid_extension(file.filename):
                return False, f"Extension non autorisée. Extensions autorisées: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            
            # Vérification du type MIME
            content = await file.read()
            await file.seek(0)  # Reset pour permettre la lecture ultérieure
            
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                return False, f"Type de fichier non autorisé: {mime_type}"
            
            # Vérification du contenu (détection de CSV valide)
            if not cls._is_valid_csv_content(content):
                return False, "Le contenu ne semble pas être un fichier CSV valide"
            
            return True, ""
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    @classmethod
    def _is_valid_extension(cls, filename: str) -> bool:
        """Vérifie si l'extension du fichier est autorisée"""
        if not filename:
            return False
        
        _, ext = os.path.splitext(filename.lower())
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def _is_valid_csv_content(cls, content: bytes) -> bool:
        """Vérifie si le contenu semble être un CSV valide"""
        try:
            # Décoder en UTF-8
            text_content = content.decode('utf-8')
            
            # Vérifier qu'il y a des virgules (séparateur CSV)
            if ',' not in text_content:
                return False
            
            # Vérifier qu'il y a des lignes
            lines = text_content.strip().split('\n')
            if len(lines) < 2:  # Au moins header + 1 ligne de données
                return False
            
            # Vérifier que la première ligne contient des virgules (header)
            if ',' not in lines[0]:
                return False
            
            return True
            
        except UnicodeDecodeError:
            return False
    
    @classmethod
    def calculate_file_hash(cls, content: bytes) -> str:
        """Calcule le hash SHA-256 d'un fichier"""
        return hashlib.sha256(content).hexdigest()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Nettoie un nom de fichier pour éviter les injections"""
        # Supprimer les caractères dangereux
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limiter la longueur
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename

async def validate_upload_file(file: UploadFile) -> None:
    """
    Valide un fichier uploadé et lève une exception si invalide
    """
    is_valid, error_message = await SecurityValidator.validate_file(file)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier invalide: {error_message}"
        ) 