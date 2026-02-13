from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

from products.models import Product
from .cart import Cart
from .functions import (
    load_db_cart_into_session,
    set_db_item_quantity,
    remove_cart_item_from_db,
    clear_user_cart_from_db,
)


def cart_detail(request):
    cart = Cart(request)
    
    print(f"\n\n\nThis is Cart:\n\n\n{cart}\n\n\n")
    return render(request, 'cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    redirect_to = request.POST.get("redirection_page") or request.META.get("HTTP_REFERER") or "cart_detail"
    
    if user.is_authenticated:
        current_qty = 0
        
        current_qty = cart.get_quantity(product)
        set_db_item_quantity(user, product.id, current_qty + 1)
        load_db_cart_into_session(request)
    else:
        cart.add(product=product, quantity=1)
    
    print(f"\n\nThis is Request.POST:\n{request.POST}\n\n\n\n{redirect_to}\n\n")
    return redirect(redirect_to)

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    action = request.POST['action']
    current_quantity = cart.get_quantity(product)
    
    if action == 'increase':
        new_qty = current_quantity + 1
    
    elif action == 'decrease':
        new_qty = current_quantity - 1
    else:
        return redirect('cart_detail')
    
    if user.is_authenticated:
        set_db_item_quantity(user, product.id, new_qty)
        load_db_cart_into_session(request)
    else:
        cart.add(product, quantity=1 if action == "increase" else -1)
    
    print(f"\n\nThis is Request.POST:\n{request.POST}\n\n")
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    user = request.user
    product = get_object_or_404(Product, id=product_id)
        
    if request.POST.get("action") == "delete":
        if user.is_authenticated:
            remove_cart_item_from_db(user, product_id)
            load_db_cart_into_session(request)
        else:
            cart.remove(product)
    
    print(request.POST)
    return redirect('cart_detail')

@require_POST
def clear_cart(request):
    cart = Cart(request)
    user = request.user
    
    if user.is_authenticated:
        clear_user_cart_from_db(user)
        load_db_cart_into_session(request)
        messages.success(request, "All products successfully removed from your cart.")
        return redirect('homepage')
    
    if cart.cart:
        cart.clear()
        messages.success(request, "All products successfully removed from your cart.")
    else:
        messages.warning(request, "Your cart is already empty.")
    
    return redirect('homepage')
