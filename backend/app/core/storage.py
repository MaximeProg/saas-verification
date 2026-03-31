"""
Module de gestion du stockage des fichiers
Pour le moment, stockage local. À remplacer par S3/Cloud Storage en production
"""
import os
import uuid
from fastapi import UploadFile
from pathlib import Path
from app.config import settings


async def upload_file(file: UploadFile, folder: str = "uploads") -> str:
    """
    Upload un fichier et retourne l'URL
    
    Args:
        file: Fichier uploadé
        folder: Dossier de destination
        
    Returns:
        URL du fichier uploadé
    """
    # Créer le dossier s'il n'existe pas
    upload_dir = Path(settings.UPLOAD_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer un nom de fichier unique
    file_extension = Path(file.filename).suffix if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Sauvegarder le fichier
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Retourner l'URL relative
    relative_path = f"{folder}/{unique_filename}"
    return f"{settings.STORAGE_URL_BASE}/{relative_path}"


def delete_file(file_url: str) -> bool:
    """
    Supprime un fichier
    
    Args:
        file_url: URL du fichier à supprimer
        
    Returns:
        True si supprimé avec succès
    """
    try:
        # Extraire le chemin relatif de l'URL
        relative_path = file_url.replace(settings.STORAGE_URL_BASE + "/", "")
        file_path = Path(settings.UPLOAD_DIR) / relative_path
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier: {e}")
        return False
