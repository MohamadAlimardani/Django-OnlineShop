from django.shortcuts import render

from products.models import Product

# Create your views here.
def index(request):
    featured_products = Product.objects.order_by("id")[:4]
    return render(request, "base/index.html", {"featured_products": featured_products})
