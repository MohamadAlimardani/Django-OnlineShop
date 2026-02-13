from django.db import transaction

from products.models import Product
from .models import UserCart, CartItem


def get_or_create_user_cart(user) -> UserCart:
    db_cart, _ = UserCart.objects.get_or_create(user=user)
    return db_cart


@transaction.atomic
def merge_session_cart_into_db(user, session_cart: dict) -> None:
    if not session_cart:
        return
    
    db_cart = get_or_create_user_cart(user)
    
    for product_id_str, item_data in session_cart.items():
        product_id = int(product_id_str)
        session_qty = int(item_data.get("quantity", 0))
        if session_qty <= 0:
            continue
    
    product = Product.objects.select_for_update().get(pk=product_id)
    
    cart_item = CartItem.objects.filter(cart=db_cart, product_id=product_id).first()
    db_qty = cart_item.quantity if cart_item else 0
    
    new_qty = db_qty + session_qty
    if new_qty > product.stock:
        new_qty = product.stock
    
    if new_qty <= 0:
        CartItem.objects.filter(cart=db_cart, product_id=product_id).delete()
    elif cart_item:
        cart_item.quantity = new_qty
        cart_item.save(update_fields=["quantity"])
    else:
        CartItem.objects.create(cart=db_cart, product_id=product_id, quantity=new_qty)

def load_db_cart_into_session(request) -> None:
    user = request.user
    if not user.is_authenticated:
        return
    
    db_cart = UserCart.objects.filter(user=user).first()
    session_cart = request.session.get("cart") or {}
    
    if not db_cart:
        request.session["cart"] = session_cart
        request.session.modified = True
        return
    
    new_session_cart = {}
    items = (
        CartItem.objects.select_related("product").filter(cart=db_cart)
    )
    for item in items:
        new_session_cart[str(item.product_id)] = {
            "quantity": item.quantity,
            "price": str(item.product.price),
        }
    
    request.session["cart"] = new_session_cart
    request.session.modified = True


@transaction.atomic
def set_db_item_quantity(user, product_id: int, quantity: int) -> None:
    db_cart = get_or_create_user_cart(user)
    product = Product.objects.select_for_update().get(pk=product_id)
    
    if quantity <= 0:
        CartItem.objects.filter(cart=db_cart, product_id=product_id).delete()
        return
    
    if quantity > product.stock:
        quantity = product.stock
    
    CartItem.objects.update_or_create(
        cart=db_cart,
        product_id=product_id,
        defaults={"quantity": quantity},
    )

def remove_cart_item_from_db(user, product_id):
    db_cart = UserCart.objects.filter(user=user).first()
    if db_cart:
        CartItem.objects.filter(cart=db_cart, product_id=product_id).delete()

def clear_user_cart_from_db(user):
    db_cart = UserCart.objects.filter(user=user).first()
    if db_cart:
        CartItem.objects.filter(cart=db_cart).delete()
