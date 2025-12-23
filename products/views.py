from django.http import Http404
from django.shortcuts import render
from .models import Product

def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def product_details(request, slug=None):
    product_detail = None
    if slug is not None:
        try:
            product_detail = Product.objects.get(slug=slug)
        except:
            raise Http404
    
    return render(request, 'product_details.html', {'product_detail': product_detail})