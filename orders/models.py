from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"
    
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    
    full_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    currency = models.CharField(max_length=10, default="IRR")
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default="0.00",
    )
    
    payment_reference = models.CharField(
        max_length=20,
        blank=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderAddress(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping_address",
    )
    
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=80)
    country = models.CharField(
        max_length=50,
        default="Iran",
    )
    
    def __str__(self):
        return f"Shipping for Order #{self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="items",
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        )
    quantity = models.PositiveIntegerField(default=1)
    
    def line_total(self):
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
