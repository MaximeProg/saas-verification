"""
Test des tasks Celery
Assurez-vous que Redis et Celery worker sont lancés
"""
import asyncio
from app.tasks.email_tasks import send_verification_initiated_email
from app.tasks.webhook_tasks import send_verification_webhook
from app.tasks.image_tasks import compress_and_upload_image
import base64


def test_email_task():
    """Test envoi email"""
    print("📧 Test envoi email...")
    
    task = send_verification_initiated_email.delay(
        recipient_email="test@example.com",
        recipient_name="Jean Dupont",
        verification_id="KYC-2026000001",
        verification_url="http://localhost:3000/session/test123"
    )
    
    print(f"   Task ID: {task.id}")
    print(f"   Status: {task.status}")
    print("   ✅ Email task lancée")
    
    return task


def test_webhook_task():
    """Test webhook"""
    print("\n🔗 Test webhook...")
    
    # Vous devez avoir une entreprise avec webhook_url configuré
    task = send_verification_webhook.delay(
        verification_id="KYC-2026000001",
        event_type="verification.approved",
        company_id="2b7b4a79-ff7e-485f-8daa-f18f19a211f4"  # ID de Test Company
    )
    
    print(f"   Task ID: {task.id}")
    print(f"   Status: {task.status}")
    print("   ✅ Webhook task lancée")
    
    return task


def test_image_task():
    """Test compression image"""
    print("\n🖼️  Test compression image...")
    
    # Créer une petite image de test
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    # Encoder en base64
    img_b64 = base64.b64encode(img_data).decode('utf-8')
    
    task = compress_and_upload_image.delay(
        verification_id="KYC-2026000001",
        image_data_base64=img_b64,
        image_type="front",
        filename="test_document"
    )
    
    print(f"   Task ID: {task.id}")
    print(f"   Status: {task.status}")
    print("   ✅ Image task lancée")
    
    return task


def check_task_status(task, timeout=10):
    """Vérifie le statut d'une task"""
    import time
    
    print(f"\n⏳ Attente résultat (max {timeout}s)...")
    
    start = time.time()
    while time.time() - start < timeout:
        if task.ready():
            if task.successful():
                print(f"   ✅ Task terminée avec succès!")
                print(f"   Résultat: {task.result}")
                return True
            else:
                print(f"   ❌ Task échouée: {task.info}")
                return False
        
        time.sleep(1)
        print(f"   Status: {task.status}...")
    
    print(f"   ⏰ Timeout - Task toujours en cours")
    return False


if __name__ == "__main__":
    print("🧪 Test des Tasks Celery\n")
    print("⚠️  Prérequis:")
    print("   1. Redis doit être lancé (localhost:6379)")
    print("   2. Celery worker doit être lancé")
    print("   3. SMTP doit être configuré dans .env (pour email)")
    print("   4. Cloudinary doit être configuré dans .env (pour images)")
    print("\n" + "="*50 + "\n")
    
    # Test email (ne nécessite pas SMTP configuré pour tester le lancement)
    email_task = test_email_task()
    
    # Test webhook
    webhook_task = test_webhook_task()
    
    # Vérifier les statuts
    print("\n" + "="*50)
    print("📊 Vérification des résultats...")
    print("="*50)
    
    check_task_status(email_task, timeout=15)
    check_task_status(webhook_task, timeout=15)
    
    print("\n🎉 Tests terminés!")
    print("\n💡 Pour voir les logs détaillés, consultez le terminal Celery worker")
