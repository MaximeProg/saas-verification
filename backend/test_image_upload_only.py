"""
Test upload Cloudinary direct (sans DB update)
"""
import cloudinary
import cloudinary.uploader
from app.config import settings
import base64
from PIL import Image
import io

# Configuration Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# Image de test 1x1 pixel
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print("Test Upload Cloudinary avec Compression\n")
print("="*60)

# Décoder
image_data = base64.b64decode(test_image_base64)
print(f"\nImage decodee: {len(image_data)} bytes")

# Compresser avec Pillow
img = Image.open(io.BytesIO(image_data))
print(f"Format original: {img.format}, Mode: {img.mode}, Taille: {img.size}")

# Convertir en RGB si nécessaire
if img.mode in ('RGBA', 'LA', 'P'):
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
    img = background

# Sauvegarder en JPEG compressé
output = io.BytesIO()
img.save(output, format='JPEG', quality=85, optimize=True)
compressed_data = output.getvalue()

print(f"Image compressee: {len(compressed_data)} bytes")

# Upload vers Cloudinary
print("\nUpload vers Cloudinary...")

try:
    result = cloudinary.uploader.upload(
        compressed_data,
        folder="kyc/test",
        public_id="test_compression",
        resource_type="image",
        format="jpg",
        transformation=[
            {"quality": "auto:good"},
            {"fetch_format": "auto"}
        ]
    )
    
    print("\nUpload reussi!")
    print(f"   URL: {result.get('secure_url')}")
    print(f"   Public ID: {result.get('public_id')}")
    print(f"   Format: {result.get('format')}")
    print(f"   Taille: {result.get('bytes')} bytes")
    print(f"   Largeur: {result.get('width')}px")
    print(f"   Hauteur: {result.get('height')}px")
    
    print("\n" + "="*60)
    print("Cloudinary + Compression = OK!")
    print("="*60)
    
except Exception as e:
    print(f"\nErreur: {e}")
    print("="*60)
