import os
import io
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import pillow_heif

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


def process_image_file(image_file, max_dimension=2000, quality=90):
    """
    Takes an uploaded image file (supports HEIC, HEIF, JPEG, PNG, WebP, etc.),
    rotates according to EXIF orientation, converts to RGB JPEG format,
    and returns a django ContentFile with .jpg extension.
    """
    if not image_file:
        return image_file

    try:
        # Seek to beginning if possible
        if hasattr(image_file, 'seek'):
            image_file.seek(0)

        # Open image with Pillow (pillow_heif allows opening .heic / .heif directly)
        img = Image.open(image_file)

        # Transpose according to EXIF orientation if present
        img = ImageOps.exif_transpose(img)

        # Convert RGBA / P / CMYK modes to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background for transparent images
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if extremely large to save bandwidth and storage while maintaining high resolution
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Save to memory as high quality JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        # Generate new safe, compact filename with .jpg extension
        import re, uuid
        orig_name = getattr(image_file, 'name', 'photo.heic')
        base_name, _ = os.path.splitext(orig_name)
        safe_base = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)[:30].strip('_') or 'phone'
        new_name = f"{safe_base}_{uuid.uuid4().hex[:6]}.jpg"

        return ContentFile(output.getvalue(), name=new_name)

    except Exception as e:
        # If conversion fails for any reason, return original file
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        return image_file
