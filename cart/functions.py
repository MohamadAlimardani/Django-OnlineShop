from .models import UserCart, CartItem

def save_cart_to_db(user, cart: dict):
    db_cart, _ = UserCart.objects.get_or_create(user=user)
    if not db_cart:
        db_cart = UserCart.objects.create(user=user)
        
    for product_id_str, quantity_dict in cart.items():
        product_id = int(product_id_str)
        quantity = quantity_dict.get('quantity')
        
        if quantity <= 0:
            CartItem.objects.filter(cart=db_cart, product_id=product_id).delete()
            continue
        
        CartItem.objects.update_or_create(
            cart=db_cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )

def remove_cart_item_from_db(user, product_id):
    db_cart = UserCart.objects.filter(user=user).first()
    if db_cart:
        CartItem.objects.filter(cart=db_cart, product_id=product_id).delete()

def clear_user_cart_from_db(user):
    db_cart = UserCart.objects.filter(user=user).first()
    if db_cart:
        CartItem.objects.filter(cart=db_cart).delete()
