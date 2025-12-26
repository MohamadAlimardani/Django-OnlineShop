from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('sign_out/', views.sign_out, name='sign_out'),
    path('otp/', views.otp_verification, name='otp_verification'),
    path('otp/resend/', views.resend_otp, name='resend_otp'),
]
