from .models import Cart


def cart(request):
    """Context processor to make cart available in all templates"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {
                'cart': cart,
                'cart_items_count': cart.total_items,
                'cart_total': cart.total_price,
            }
        except Cart.DoesNotExist:
            return {
                'cart': None,
                'cart_items_count': 0,
                'cart_total': 0,
            }
    return {
        'cart': None,
        'cart_items_count': 0,
        'cart_total': 0,
    }


