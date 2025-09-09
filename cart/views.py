from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from .models import Cart, CartItem
from store.models import Product


@login_required
def cart_view(request):
    """View for displaying the user's cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """Add product to cart"""
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check stock availability
        if quantity > product.stock_quantity:
            messages.error(request, f'Only {product.stock_quantity} items available in stock.')
            return redirect('store:product_detail', slug=product.slug)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item = cart.add_item(product, quantity)
        
        messages.success(request, f'{product.name} added to cart successfully!')

        # AJAX detection: prefer X-Requested-With header
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_total': cart.total_items,
                'cart_subtotal': float(cart.total_price),
            })

        return redirect('cart:cart_view')
        
    except (ValueError, Product.DoesNotExist) as e:
        messages.error(request, 'Invalid product or quantity.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid product or quantity.'})
        return redirect('store:product_list')


@login_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update quantity of a cart item"""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock availability
        if quantity > cart_item.product.stock_quantity:
            messages.error(request, f'Only {cart_item.product.stock_quantity} items available in stock.')
            return redirect('cart:cart_view')
        
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, 'Cart updated successfully!')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully!',
                'item_id': cart_item.id,
                'item_total': float(cart_item.total_price),
                'cart_total': cart_item.cart.total_items,
                'cart_subtotal': float(cart_item.cart.total_price)
            })
        
        return redirect('cart:cart_view')
        
    except (ValueError, CartItem.DoesNotExist) as e:
        messages.error(request, 'Invalid item or quantity.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid item or quantity.'})
        return redirect('cart:cart_view')


@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'{product_name} removed from cart.')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart.',
                'cart_total': cart.total_items,
                'cart_subtotal': float(cart.total_price)
            })
        
        return redirect('cart:cart_view')
        
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Item not found in cart.'})
        return redirect('cart:cart_view')


@login_required
@require_http_methods(["POST"])
def clear_cart(request):
    """Clear all items from cart"""
    try:
        cart = get_object_or_404(Cart, user=request.user)
        cart.clear()
        
        messages.success(request, 'Cart cleared successfully!')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cart cleared successfully!'
            })
        
        return redirect('cart:cart_view')
        
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Cart not found.'})
        return redirect('cart:cart_view')


@require_http_methods(["GET"])
def cart_count(request):
    """API endpoint to get cart item count"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    
    return JsonResponse({'count': count})

