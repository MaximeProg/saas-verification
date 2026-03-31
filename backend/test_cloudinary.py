"""
Test de connexion et upload Cloudinary
À exécuter après avoir configuré les credentials dans .env
"""
import cloudinary
import cloudinary.uploader
from app.config import settings
from PIL import Image
import os


def test_cloudinary_config():
    """Vérifie que les credentials sont configurés"""
    print("🔍 Vérification configuration Cloudinary...")
    
    if not settings.CLOUDINARY_CLOUD_NAME:
        print("   ❌ CLOUDINARY_CLOUD_NAME manquant dans .env")
        return False
    
    if not settings.CLOUDINARY_API_KEY:
        print("   ❌ CLOUDINARY_API_KEY manquant dans .env")
        return False
    
    if not settings.CLOUDINARY_API_SECRET:
        print("   ❌ CLOUDINARY_API_SECRET manquant dans .env")
        return False
    
    print(f"   ✅ Cloud Name: {settings.CLOUDINARY_CLOUD_NAME}")
    print(f"   ✅ API Key: {settings.CLOUDINARY_API_KEY[:10]}...")
    print(f"   ✅ API Secret: {settings.CLOUDINARY_API_SECRET[:10]}...")
    
    return True


def test_cloudinary_connection():
    """Test la connexion à Cloudinary"""
    print("\n🔗 Test connexion Cloudinary...")
    
    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        # Test avec un upload simple
        print(f"   ✅ Configuration chargée")
        print(f"   ✅ Cloud: {settings.CLOUDINARY_CLOUD_NAME}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return False


def test_cloudinary_upload():
    """Test upload d'une image"""
    print("\n📤 Test upload image...")
    
    try:
        # Créer une image de test
        img = Image.new('RGB', (200, 200), color='blue')
        test_file = 'test_cloudinary_upload.jpg'
        img.save(test_file)
        print(f"   ✅ Image test créée: {test_file}")
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            test_file,
            folder='kyc/test',
            public_id='test_upload',
            resource_type='image',
            format='jpg',
            transformation=[
                {"quality": "auto:good"},
                {"fetch_format": "auto"}
            ]
        )
        
        # Supprimer fichier local
        os.remove(test_file)
        
        print(f"   ✅ Upload réussi!")
        print(f"   📍 Public ID: {result['public_id']}")
        print(f"   🔗 URL: {result['secure_url']}")
        print(f"   📏 Taille: {result['bytes']} bytes")
        print(f"   📐 Dimensions: {result['width']}x{result['height']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur upload: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False


def test_cloudinary_compression():
    """Test compression d'image"""
    print("\n🗜️  Test compression image...")
    
    try:
        # Créer une grande image
        img = Image.new('RGB', (3000, 3000), color='red')
        test_file = 'test_large.jpg'
        img.save(test_file, quality=100)
        
        original_size = os.path.getsize(test_file)
        print(f"   📏 Taille originale: {original_size / 1024:.1f} KB")
        
        # Upload avec compression
        result = cloudinary.uploader.upload(
            test_file,
            folder='kyc/test',
            public_id='test_compression',
            transformation=[
                {"width": 2048, "height": 2048, "crop": "limit"},
                {"quality": "auto:good"},
                {"fetch_format": "auto"}
            ]
        )
        
        os.remove(test_file)
        
        compressed_size = result['bytes']
        print(f"   📏 Taille compressée: {compressed_size / 1024:.1f} KB")
        print(f"   📐 Dimensions: {result['width']}x{result['height']}")
        print(f"   💾 Économie: {(1 - compressed_size/original_size)*100:.1f}%")
        print(f"   🔗 URL: {result['secure_url']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False


if __name__ == "__main__":
    print("🧪 Test Cloudinary\n")
    print("="*60)
    
    # Test 1: Configuration
    if not test_cloudinary_config():
        print("\n❌ Configuration manquante!")
        print("\n📝 Actions requises:")
        print("   1. Créer compte sur https://cloudinary.com/users/register/free")
        print("   2. Copier Cloud Name, API Key, API Secret")
        print("   3. Ajouter dans .env")
        print("\n📖 Voir CLOUDINARY_SETUP.md pour le guide complet")
        exit(1)
    
    # Test 2: Connexion
    if not test_cloudinary_connection():
        print("\n❌ Connexion échouée!")
        print("\n📝 Vérifier les credentials dans .env")
        exit(1)
    
    # Test 3: Upload simple
    if not test_cloudinary_upload():
        print("\n❌ Upload échoué!")
        exit(1)
    
    # Test 4: Compression
    if not test_cloudinary_compression():
        print("\n❌ Compression échouée!")
        exit(1)
    
    print("\n" + "="*60)
    print("🎉 Tous les tests Cloudinary réussis!")
    print("\n✅ Cloudinary est prêt à être utilisé")
    print("📁 Vérifiez votre Media Library: https://cloudinary.com/console/media_library")
