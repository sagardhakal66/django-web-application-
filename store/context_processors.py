from django.conf import settings
from .models import Category

def categories(request):
    """
    Make categories available to all templates
    """
    return {
        'categories': Category.objects.all()
    }

def currency_settings(request):
    """
    Add US Dollars currency settings to all templates
    """
    return {
        'CURRENCY_SYMBOL': settings.CURRENCY_SYMBOL,
        'CURRENCY_CODE': settings.CURRENCY_CODE,
        'CURRENCY_NAME': settings.CURRENCY_NAME,
        'CURRENCY_SYMBOL_HTML': settings.CURRENCY_SYMBOL_HTML,
        'DECIMAL_PLACES': settings.DECIMAL_PLACES,
    }