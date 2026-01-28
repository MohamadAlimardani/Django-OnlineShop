from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from products.models import Product
from cart.cart import Cart
from .models import Order, OrderItem, OrderAddress


@dataclass(frozen=True)
class CustomerInfo:
    full_name: str
    phone_number: str = ""
    email: str = ""


@dataclass(frozen=True)
class ShippingInfo:
    address_line_1: str
    address_line_2: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "Iran"

def _iter_cart_lines(cart: Cart) -> Iterable[tuple[int, int]]:
    for item in cart:
        product = item.get("product")
        qty = item.get("quantity")
        
        if not isinstance(product, Product):
            raise ValidationError("Cart item has an invalid product.")
        
        if qty is None:
            raise ValidationError("Cart item is missing quantity.")
        
        qty = int(qty)
        if qty <=0:
            raise ValidationError("Cart contains an invalid quantity.")
        
        yield product.id, qty

@transaction.atomic
def create_order_from_cart(
    *,
    user,
    cart: Cart,
    customer: CustomerInfo,
    shipping: ShippingInfo,
    currency: str = "IRR",
    ) -> Order:
    
    lines = list(_iter_cart_lines(cart))
    if not lines:
        raise ValidationError("Your cart is empty.")
    
    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        full_name=customer.full_name.strip(),
        phone_number=customer.phone_number.strip(),
        email=customer.email.strip(),
        currency=currency,
    )
    
    OrderAddress.objects.create(
        order=Order,
        address_line_1=shipping.address_line_1.strip(),
        address_line_2=shipping.address_line_2.strip(),
        city=shipping.city.strip(),
        postal_code=shipping.postal_code.strip(),
        country=(shipping.country.strip() or "Iran"),
    )
    
    subtotal = Decimal("0.00")
    
    for product_id, qty in lines:
        product = Product.objects.select_for_update().get(pk=product_id)
        
        if product.stock < qty:
            raise ValidationError(
                f"Not enough stock for '{product.name}'. Available: {product.stock}"
            )
        
        Product.objects.filter(pk=product_id).update(stock=F("stock") - qty)
        
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_price=product.price,
            quantity=qty,
        )
        
        subtotal += product.price * qty
    
    order.subtotal = subtotal
    order.total = subtotal              # ! no shipping / discount / tax YET!
    order.save(update_fields=["subtotal", "total"])
    
    return order


@transaction.atomic
def mark_order_paid(
    *,
    order: Order,
    payment_reference: str = ""    
    ) -> Order:
    
    if order.status != Order.Status.PENDING:
        raise ValidationError("Only pending orders can be marked as paid.")
    
    order.status = Order.Status.PAID
    order.payment_reference = payment_reference.strip()
    order.save(update_fields=["status", "payment_reference", "updated_at"])
    
    return order


@transaction.atomic
def mark_order_cancel(*, order: Order) -> Order:
    if order.status != Order.Status.CANCELLED:
        raise ValidationError("Only pending order can be cancelled.")
    
    for item in order.items.all():
        Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
    
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    
    return order
