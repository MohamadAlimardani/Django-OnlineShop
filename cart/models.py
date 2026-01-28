from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from products.models import Product


class UserCart(models.Model):
    user = models.ForeignKey(
        verbose_name=_('User'),
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="cart",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        verbose_name=_('Cart'),
        to=UserCart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    
    product = models.ForeignKey(
        verbose_name=_('Product'),
        to=Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    
    quantity = models.PositiveSmallIntegerField(
        verbose_name=_('Quantity'),
        validators=[MinValueValidator(1)],
        default=1
    )
    
    class Meta:
        # unique_together = [['cart', 'product']] # ! is deprecated since Django 4.2
        
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ]
    
    def subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.price} x {self.quantity}"
