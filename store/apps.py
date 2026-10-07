from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            pass
