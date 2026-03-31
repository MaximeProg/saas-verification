"""
Test simple des webhooks avec Celery
"""
from app.tasks.webhook_tasks import send_verification_webhook
import time


print("Test Webhook Simple\n")
print("="*60)

# Utiliser les données de test existantes
verification_id = "KYC-2026000001"
company_id = "2b7b4a79-ff7e-485f-8daa-f18f19a211f4"  # Test Company

print("📋 Paramètres:")
print(f"   Verification: {verification_id}")
print(f"   Company ID: {company_id}")
print(f"   Event: verification.approved")

print("\n🔗 Lancement task webhook...")

# Lancer la task
task = send_verification_webhook.delay(
    verification_id=verification_id,
    event_type="verification.approved",
    company_id=company_id
)

print(f"   ✅ Task lancée: {task.id}")
print(f"   Status: {task.status}")

# Attendre et vérifier
print("\n⏳ Attente exécution (15s max)...\n")

for i in range(15):
    time.sleep(1)
    status = task.status
    
    if status == "PENDING":
        icon = "[WAIT]"
    elif status == "STARTED":
        icon = "[RUN]"
    elif status == "SUCCESS":
        icon = "[OK]"
    elif status == "FAILURE":
        icon = "[ERR]"
    else:
        icon = "[???]"
    
    print(f"   [{i+1:2d}s] {icon} {status}")
    
    if task.ready():
        print("\n" + "="*60)
        if task.successful():
            print("WEBHOOK ENVOYE AVEC SUCCES!")
            print(f"\nResultat:")
            result = task.result
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   {result}")
        else:
            print("WEBHOOK ECHOUE!")
            print(f"\nErreur:")
            print(f"   {task.info}")
        
        print("\n" + "="*60)
        break
else:
    print("\n" + "="*60)
    print("Task toujours en cours apres 15s")
    print("\nLa task continue en background")
    print("   Consultez les logs Celery pour voir l'execution")
    print("="*60)

print("\nNotes:")
print("   - Les webhooks necessitent que l'entreprise ait webhook_url configure")
print("   - Les logs sont stockes dans la table webhook_logs")
print("   - Retry automatique : 5 tentatives avec backoff exponentiel")
print("\nPour tester avec une vraie URL:")
print("   1. Aller sur https://webhook.site")
print("   2. Copier votre URL unique")
print("   3. Configurer dans l'entreprise (via API ou DB)")
print("   4. Relancer ce test")
