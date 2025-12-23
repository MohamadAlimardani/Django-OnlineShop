from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .cart import Cart

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart.add(product=product, quantity=1)
    
    return redirect('cart_detail')

def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    action = request.POST['action']
    current_quantity = cart.get_quantity(product)
    
    if action == 'increase':
        if current_quantity < product.stock:
            cart.add(product, quantity=1, override_quantity=False)
    
    elif action == 'decrease':
        if current_quantity > 1:
            cart.add(product, quantity=-1, override_quantity=False)
    
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    action = request.POST['action']
    
    if action == 'delete':
        cart.remove(product)
    
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    return render(request, 'cart_detail.html', {'cart': cart})
