from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock' ,'category' , 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'category')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at', 'price', 'name')
    list_per_page = 20
