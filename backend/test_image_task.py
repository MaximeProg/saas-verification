"""
Test de la task Celery de compression et upload d'image
"""
from app.tasks.image_tasks import compress_and_upload_image
import time
import base64


# Créer une petite image de test (1x1 pixel PNG)
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print("Test Task Celery - Compression et Upload Image\n")
print("="*60)

print("\nParametres:")
print(f"   Image: 1x1 pixel PNG (test)")
print(f"   Taille base64: {len(test_image_base64)} chars")

print("\nLancement task Celery...")

# Lancer la task
task = compress_and_upload_image.delay(
    verification_id="KYC-2026000001",
    image_data_base64=test_image_base64,
    image_type="front",
    filename="test_celery_image.png"
)

print(f"   Task lancee: {task.id}")
print(f"   Status: {task.status}")

# Attendre et vérifier
print("\nAttente execution (20s max)...\n")

for i in range(20):
    time.sleep(1)
    status = task.status
    
    icon = {
        "PENDING": "[WAIT]",
        "STARTED": "[RUN]",
        "SUCCESS": "[OK]",
        "FAILURE": "[ERR]",
        "RETRY": "[RETRY]"
    }.get(status, "[???]")
    
    print(f"   [{i+1:2d}s] {icon} {status}")
    
    if task.ready():
        print("\n" + "="*60)
        if task.successful():
            print("IMAGE UPLOADEE AVEC SUCCES!\n")
            result = task.result
            print("Resultat:")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   {result}")
            
            print("\nVerifiez l'image sur Cloudinary:")
            print("   https://cloudinary.com/console/media_library")
        else:
            print("UPLOAD ECHOUE!\n")
            print("Erreur:")
            print(f"   {task.info}")
        
        print("\n" + "="*60)
        break
else:
    print("\n" + "="*60)
    print("Task toujours en cours apres 20s")
    print("\nConsultez les logs Celery")
    print("="*60)

print("\nNotes:")
print("   - La task compresse l'image avec Pillow")
print("   - Upload vers Cloudinary dans le folder 'kyc'")
print("   - Retourne l'URL publique de l'image")
