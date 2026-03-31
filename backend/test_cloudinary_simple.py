"""
Test Cloudinary simplifié - Vérification credentials
"""
import cloudinary
import cloudinary.uploader
from app.config import settings


print("🧪 Test Cloudinary Simple\n")
print("="*60)

# Configuration
print("🔧 Configuration...")
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

print(f"   Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
print(f"   API Key: {settings.CLOUDINARY_API_KEY[:10]}...")
print(f"   ✅ Configuration chargée\n")

# Test upload avec unsigned preset (si configuré)
print("📤 Test upload...")

try:
    # Créer image test
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='green')
    img.save('test.jpg')
    
    # Upload
    result = cloudinary.uploader.upload(
        'test.jpg',
        folder='kyc-test',
        use_filename=True,
        unique_filename=True
    )
    
    print(f"   ✅ Upload réussi!")
    print(f"   🔗 URL: {result['secure_url']}")
    print(f"   📏 Taille: {result['bytes']} bytes")
    
    # Nettoyer
    import os
    os.remove('test.jpg')
    
    print("\n" + "="*60)
    print("🎉 Cloudinary fonctionne parfaitement!")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    print("\n💡 Solutions possibles:")
    print("   1. Vérifier que les credentials sont corrects")
    print("   2. Aller dans Cloudinary Settings → Security")
    print("   3. Vérifier 'Upload presets' ou 'Restricted media types'")
    print("   4. Essayer avec un nouveau compte Cloudinary")
    
    import os
    if os.path.exists('test.jpg'):
        os.remove('test.jpg')
