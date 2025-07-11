"""
URL Configuration for inventory_project
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('equipment/', include('equipment.urls')),
    path('', RedirectView.as_view(url='equipment/dashboard/', permanent=True)),
    path('health/', include('inventory_project.health_urls')),
]
