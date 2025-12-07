from .models import Cart

def cart(request):
    """
    Make cart information available to all templates
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {
                'cart': cart,
                'cart_items_count': cart.get_total_quantity()
            }
        except Cart.DoesNotExist:
            return {
                'cart': None,
                'cart_items_count': 0
            }
    return {
        'cart': None,
        'cart_items_count': 0
    }