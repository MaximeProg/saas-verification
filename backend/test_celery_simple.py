"""
Test simple des tasks Celery sans dépendances externes
"""
from app.tasks.webhook_tasks import send_verification_webhook
import time


def test_webhook_task():
    """Test webhook task"""
    print("🔗 Test webhook task...")
    
    # Lancer la task
    task = send_verification_webhook.delay(
        verification_id="KYC-2026000001",
        event_type="verification.approved",
        company_id="2b7b4a79-ff7e-485f-8daa-f18f19a211f4"
    )
    
    print(f"   ✅ Task lancée: {task.id}")
    print(f"   Status initial: {task.status}")
    
    # Attendre un peu
    print("\n   ⏳ Attente exécution (5s)...")
    time.sleep(5)
    
    print(f"   Status après 5s: {task.status}")
    
    if task.ready():
        if task.successful():
            print(f"   ✅ Résultat: {task.result}")
        else:
            print(f"   ❌ Erreur: {task.info}")
    else:
        print(f"   ⏳ Task toujours en cours...")
    
    return task


if __name__ == "__main__":
    print("🧪 Test Simple Celery\n")
    print("="*50)
    
    task = test_webhook_task()
    
    print("\n" + "="*50)
    print("✅ Test terminé!")
    print(f"\n💡 Task ID: {task.id}")
    print("💡 Consultez les logs Celery worker pour voir l'exécution")
