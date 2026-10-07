# Ensure pillow-heif is registered at Python / Django initialization
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass
