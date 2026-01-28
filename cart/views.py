from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

from products.models import Product
from .cart import Cart
from .functions import save_cart_to_db, remove_cart_item_from_db, clear_user_cart_from_db


def cart_detail(request):
    cart = Cart(request)
    
    print(f"\n\n\nThis is Cart:\n\n\n{cart}\n\n\n")
    return render(request, 'cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    current_page: str = request.POST.get('current_page') or request.META.get('HTTP_REFERER')
    
    cart.add(product=product, quantity=1)
    if user.is_authenticated:
        save_cart_to_db(user, cart.cart)
    
    print(f"\n\nThis is Request.POST:\n{request.POST}\n\n{current_page}\n\n")
    
    if current_page and url_has_allowed_host_and_scheme(current_page, allowed_hosts={request.get_host()}):
        return redirect(current_page)
    return redirect("cart_detail")

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    action = request.POST['action']
    current_quantity = cart.get_quantity(product)
    
    if action == 'increase':
        if current_quantity < product.stock:
            cart.add(product, quantity=1)
    
    elif action == 'decrease':
        if current_quantity > 1:
            cart.add(product, quantity=-1)
    
    print(f"\n\nThis is Request.POST:\n{request.POST}\n\n")
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    action = request.POST['action']
    
    if action == 'delete':
        cart.remove(product)
        if user.is_authenticated:
            remove_cart_item_from_db(user, product_id)
    
    print(request.POST)
    return redirect('cart_detail')

@require_POST
def clear_cart(request):
    cart = Cart(request)
    user = request.user
    
    if len(cart):
        cart.clear()
        if user.is_authenticated:
            clear_user_cart_from_db(user)
        messages.success(request, "All products successfully removed from your cart.")
    else:
        messages.warning(request, "You're cart is already empty.")
        return redirect('cart_detail')
    return redirect('homepage')
