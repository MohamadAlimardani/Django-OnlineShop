from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Basic Info", {"fields": ("name", "image", "category", "slug")}),
        ("Pricing & Stock", {"fields": ("price", "stock")}),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    prepopulated_fields = {'slug': ('name', 'category')}
    
    list_display = ('id', 'name', 'price', 'stock', 'category')
    
    list_select_related = ("category",)
    
    list_display_links = ('id', 'name')
    
    list_editable = ('price', 'stock')
    
    list_filter = ('created_at', 'updated_at', 'price')
    
    search_fields = ('name', 'description', 'category')
    
    ordering = ('-created_at', 'price', 'name')
    
    list_per_page = 25
    
    inlines = [ProductImageInline]
