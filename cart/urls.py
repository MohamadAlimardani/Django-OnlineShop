from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>', views.cart_update, name='cart_update'),
    path('clear/', views.clear_cart, name='clear_cart'),
]
