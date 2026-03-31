"""
Test de connexion et envoi SMTP
À exécuter après avoir configuré les credentials dans .env
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def test_smtp_config():
    """Vérifie que les credentials SMTP sont configurés"""
    print("🔍 Vérification configuration SMTP...")
    
    if not settings.SMTP_HOST:
        print("   ❌ SMTP_HOST manquant dans .env")
        return False
    
    if not settings.SMTP_USER:
        print("   ❌ SMTP_USER manquant dans .env")
        return False
    
    if not settings.SMTP_PASSWORD:
        print("   ❌ SMTP_PASSWORD manquant dans .env")
        return False
    
    print(f"   ✅ Host: {settings.SMTP_HOST}")
    print(f"   ✅ Port: {settings.SMTP_PORT}")
    print(f"   ✅ User: {settings.SMTP_USER}")
    print(f"   ✅ From: {settings.SMTP_FROM_EMAIL or settings.SMTP_USER}")
    
    return True


def test_smtp_connection():
    """Test la connexion au serveur SMTP"""
    print("\n🔗 Test connexion SMTP...")
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            print("   ✅ TLS activé")
            
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            print("   ✅ Authentification réussie")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Erreur authentification: {e}")
        print("   💡 Vérifiez que vous utilisez un App Password (pas votre mot de passe Gmail)")
        return False
        
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return False


def test_smtp_send():
    """Test envoi d'un email simple"""
    print("\n📧 Test envoi email...")
    
    try:
        # Créer message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🧪 Test KYC Platform"
        msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = settings.SMTP_USER  # Envoi à soi-même
        
        # Contenu texte
        text = """
        Test email depuis KYC Platform
        
        Si vous recevez cet email, la configuration SMTP fonctionne correctement !
        """
        
        # Contenu HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
                .content { background: #f9fafb; padding: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Test KYC Platform</h1>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Si vous recevez cet email, la configuration SMTP fonctionne correctement !</p>
                    <p><strong>✅ Configuration validée</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Envoyer
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"   ✅ Email envoyé à {settings.SMTP_USER}")
        print("   📬 Vérifiez votre boîte email (peut prendre 10-30 secondes)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur envoi: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Test SMTP Gmail\n")
    print("="*60)
    
    # Test 1: Configuration
    if not test_smtp_config():
        print("\n❌ Configuration manquante!")
        print("\n📝 Actions requises:")
        print("   1. Activer 2FA sur Gmail")
        print("   2. Créer App Password: https://myaccount.google.com/apppasswords")
        print("   3. Ajouter dans .env:")
        print("      SMTP_HOST=smtp.gmail.com")
        print("      SMTP_PORT=587")
        print("      SMTP_USER=votre_email@gmail.com")
        print("      SMTP_PASSWORD=votre_app_password")
        print("\n📖 Voir SMTP_SETUP.md pour le guide complet")
        exit(1)
    
    # Test 2: Connexion
    if not test_smtp_connection():
        print("\n❌ Connexion échouée!")
        print("\n📝 Vérifier:")
        print("   - App Password correct (16 caractères sans espaces)")
        print("   - 2FA activé sur Gmail")
        print("   - Connexion internet active")
        exit(1)
    
    # Test 3: Envoi
    if not test_smtp_send():
        print("\n❌ Envoi échoué!")
        exit(1)
    
    print("\n" + "="*60)
    print("🎉 Tous les tests SMTP réussis!")
    print("\n✅ SMTP est prêt à être utilisé")
    print("📧 Vérifiez votre boîte email")
