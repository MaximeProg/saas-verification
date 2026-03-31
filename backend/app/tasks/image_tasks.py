from celery import Task
from PIL import Image
import io
import cloudinary
import cloudinary.uploader
from typing import Optional
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.config import settings
from app.models.verification import Verification


# Configuration Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


class ImageCompressionTask(Task):
    """Task de base pour compression d'images"""
    
    def compress_image(self, image_data: bytes, quality: int = 85, max_size: tuple = (2048, 2048)) -> bytes:
        """
        Compresse une image
        
        Args:
            image_data: Données de l'image
            quality: Qualité JPEG (1-100)
            max_size: Taille maximale (width, height)
        
        Returns:
            bytes: Image compressée
        """
        # Ouvrir l'image
        img = Image.open(io.BytesIO(image_data))
        
        # Convertir en RGB si nécessaire (pour JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Redimensionner si nécessaire
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compresser
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output.read()


@celery_app.task(
    bind=True,
    base=ImageCompressionTask,
    name="app.tasks.image_tasks.compress_and_upload_image",
    max_retries=3,
    default_retry_delay=60
)
def compress_and_upload_image(
    self,
    verification_id: str,
    image_data_base64: str,
    image_type: str,
    filename: str
):
    """
    Compresse et upload une image vers Cloudinary
    
    Args:
        verification_id: ID de la vérification
        image_data_base64: Image encodée en base64
        image_type: Type d'image (front, back, selfie)
        filename: Nom du fichier
    """
    import base64
    
    try:
        # Décoder base64
        image_data = base64.b64decode(image_data_base64)
        
        # Compresser l'image
        compressed_data = self.compress_image(image_data, quality=85)
        
        # Upload vers Cloudinary
        folder = f"kyc/{verification_id}"
        
        result = cloudinary.uploader.upload(
            compressed_data,
            folder=folder,
            public_id=f"{image_type}_{filename}",
            resource_type="image",
            format="jpg",
            transformation=[
                {"quality": "auto:good"},
                {"fetch_format": "auto"}
            ]
        )
        
        # URL sécurisée
        secure_url = result.get("secure_url")
        
        # Mettre à jour la vérification dans la DB (synchrone)
        sync_engine = create_engine(
            settings.DATABASE_URL.replace("+asyncpg", "").replace("?sslmode=require&channel_binding=require", ""),
            connect_args={"sslmode": "require"}
        )
        Session = sessionmaker(bind=sync_engine)
        
        try:
            with Session() as db:
                field_map = {
                    "front": "document_front_url",
                    "back": "document_back_url",
                    "selfie": "selfie_url"
                }
                
                field_name = field_map.get(image_type)
                if field_name:
                    db.execute(
                        update(Verification)
                        .where(Verification.verification_id == verification_id)
                        .values(**{field_name: secure_url})
                    )
                    db.commit()
        except Exception as e:
            raise Exception(f"Failed to update verification: {e}")
        finally:
            sync_engine.dispose()
        
        return {
            "success": True,
            "url": secure_url,
            "verification_id": verification_id,
            "image_type": image_type
        }
        
    except Exception as exc:
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    name="app.tasks.image_tasks.process_verification_documents",
    max_retries=3
)
def process_verification_documents(
    verification_id: str,
    front_data_base64: str,
    back_data_base64: Optional[str] = None,
    selfie_data_base64: Optional[str] = None
):
    """
    Traite tous les documents d'une vérification
    Lance des sous-tasks pour chaque image
    """
    from celery import group
    
    tasks = []
    
    # Document recto
    tasks.append(
        compress_and_upload_image.s(
            verification_id,
            front_data_base64,
            "front",
            "document_front"
        )
    )
    
    # Document verso (optionnel)
    if back_data_base64:
        tasks.append(
            compress_and_upload_image.s(
                verification_id,
                back_data_base64,
                "back",
                "document_back"
            )
        )
    
    # Selfie (optionnel)
    if selfie_data_base64:
        tasks.append(
            compress_and_upload_image.s(
                verification_id,
                selfie_data_base64,
                "selfie",
                "selfie"
            )
        )
    
    # Exécuter toutes les tasks en parallèle
    job = group(tasks)
    result = job.apply_async()
    
    return {
        "success": True,
        "verification_id": verification_id,
        "tasks_count": len(tasks),
        "group_id": result.id
    }
