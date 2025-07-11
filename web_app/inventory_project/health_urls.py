"""
Health check URLs for inventory project
"""
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    path('', health_check, name='health_check'),
]
