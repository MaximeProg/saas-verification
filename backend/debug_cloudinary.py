"""
Debug Cloudinary - Vérifier configuration et permissions
"""
import cloudinary
import cloudinary.uploader
from app.config import settings
import json


print("🔍 Debug Cloudinary\n")
print("="*60)

# Configuration
print("📋 Configuration actuelle:")
print(f"   Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
print(f"   API Key: {settings.CLOUDINARY_API_KEY}")
print(f"   API Secret: {settings.CLOUDINARY_API_SECRET[:10]}...{settings.CLOUDINARY_API_SECRET[-5:]}")

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

print("\n✅ Configuration chargée\n")

# Test 1: Upload avec options minimales
print("="*60)
print("🧪 Test 1: Upload basique")
print("="*60)

try:
    from PIL import Image
    import os
    
    # Créer image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save('test_basic.jpg')
    
    # Upload le plus simple possible
    result = cloudinary.uploader.upload('test_basic.jpg')
    
    print(f"✅ Upload réussi!")
    print(f"   Public ID: {result['public_id']}")
    print(f"   URL: {result['secure_url']}")
    
    os.remove('test_basic.jpg')
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print(f"\n📋 Détails erreur:")
    print(f"   Type: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    
    if os.path.exists('test_basic.jpg'):
        os.remove('test_basic.jpg')

# Test 2: Upload avec folder
print("\n" + "="*60)
print("🧪 Test 2: Upload avec folder")
print("="*60)

try:
    img = Image.new('RGB', (100, 100), color='red')
    img.save('test_folder.jpg')
    
    result = cloudinary.uploader.upload(
        'test_folder.jpg',
        folder='kyc'
    )
    
    print(f"✅ Upload réussi!")
    print(f"   Public ID: {result['public_id']}")
    print(f"   URL: {result['secure_url']}")
    
    os.remove('test_folder.jpg')
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    
    if os.path.exists('test_folder.jpg'):
        os.remove('test_folder.jpg')

# Test 3: Upload avec toutes les options
print("\n" + "="*60)
print("🧪 Test 3: Upload avec transformations")
print("="*60)

try:
    img = Image.new('RGB', (500, 500), color='green')
    img.save('test_full.jpg')
    
    result = cloudinary.uploader.upload(
        'test_full.jpg',
        folder='kyc/test',
        public_id='test_full',
        resource_type='image',
        type='upload',
        overwrite=True,
        invalidate=True,
        transformation=[
            {"quality": "auto:good"},
            {"fetch_format": "auto"}
        ]
    )
    
    print(f"✅ Upload réussi!")
    print(f"   Public ID: {result['public_id']}")
    print(f"   URL: {result['secure_url']}")
    print(f"   Format: {result['format']}")
    print(f"   Taille: {result['bytes']} bytes")
    
    os.remove('test_full.jpg')
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print(f"\n📋 Message complet:")
    print(f"   {str(e)}")
    
    if os.path.exists('test_full.jpg'):
        os.remove('test_full.jpg')

print("\n" + "="*60)
print("📊 Résumé")
print("="*60)
print("\n💡 Si tous les tests échouent avec 'missing permissions':")
print("   1. Aller sur https://cloudinary.com/console")
print("   2. Settings → Security")
print("   3. Désactiver toutes les restrictions")
print("   4. Ou créer un nouveau compte gratuit sans restrictions")
