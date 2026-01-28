from django.shortcuts import render

from products.models import Product

def homepage(request):
    featured_products = Product.objects.order_by("id")[:4]
    return render(request, "components/homepage.html", {"featured_products": featured_products})
