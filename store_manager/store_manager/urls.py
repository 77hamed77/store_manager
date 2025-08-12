# store_manager/urls.py
from django.contrib import admin
from django.urls import path, include # تأكد من إضافة include هنا

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')), # أضف هذا السطر
]