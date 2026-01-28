from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)

    description = models.TextField(max_length=1000)

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveSmallIntegerField()

    image = models.ImageField(upload_to="Products_Images/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(unique=True, max_length=255)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to="Products_Images/Gallery")

    alt = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.product.name}'s Image."
