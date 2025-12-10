from .models import Cart
from django.conf import settings

def cart(request):
    """
    Make cart information available to all templates
    """
    if request.user.is_authenticated:
        try:
            cart_obj = Cart.objects.get(user=request.user)
            return {
                'cart': cart_obj,
                'cart_items_count': cart_obj.get_total_quantity(),
                # ============ UPDATED FOR USD CURRENCY ============
                'cart_total': cart_obj.get_total_price_display(),  # $1,350.00
                'cart_total_no_decimal': cart_obj.get_total_price_no_decimal(),  # $1,350
                'cart_total_raw': cart_obj.get_total_price(),  # 1350.00 (for calculations)
                'cart_items': cart_obj.items.all(),  # Added for easy access
                'cart_currency_symbol': settings.CURRENCY_SYMBOL,  # $
                'cart_currency_code': settings.CURRENCY_CODE,  # USD
                # ===================================================
            }
        except Cart.DoesNotExist:
            return {
                'cart': None,
                'cart_items_count': 0,
                # ============ UPDATED FOR USD CURRENCY ============
                'cart_total': f"{settings.CURRENCY_SYMBOL}0.00",
                'cart_total_no_decimal': f"{settings.CURRENCY_SYMBOL}0",
                'cart_total_raw': 0,
                'cart_items': [],
                'cart_currency_symbol': settings.CURRENCY_SYMBOL,
                'cart_currency_code': settings.CURRENCY_CODE,
                # ===================================================
            }
    
    # For anonymous users
    return {
        'cart': None,
        'cart_items_count': 0,
        # ============ UPDATED FOR USD CURRENCY ============
        'cart_total': f"{settings.CURRENCY_SYMBOL}0.00",
        'cart_total_no_decimal': f"{settings.CURRENCY_SYMBOL}0",
        'cart_total_raw': 0,
        'cart_items': [],
        'cart_currency_symbol': settings.CURRENCY_SYMBOL,
        'cart_currency_code': settings.CURRENCY_CODE,
        # ===================================================
    }