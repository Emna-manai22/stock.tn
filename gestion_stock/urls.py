# gestion_stock/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),            # redirige vers login
    path('', include('stockapp.urls')),                      # inclut TOUTES les urls de stockapp
    path('admin/', admin.site.urls),
]
