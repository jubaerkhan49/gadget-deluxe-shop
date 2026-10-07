from store.models import StoreSettings, IPhoneModel
from django.utils.translation import get_language


def store_settings_context(request):
    current_lang = get_language() or 'en'
    is_bn = current_lang.startswith('bn')
    
    settings = StoreSettings.get_settings()
    models_nav = IPhoneModel.objects.filter(is_active=True).order_by('order')

    return {
        'store_settings': settings,
        'nav_models': models_nav,
        'current_language': current_lang,
        'is_bangla': is_bn,
    }
