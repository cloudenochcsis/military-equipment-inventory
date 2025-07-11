"""
Context processors for inventory project templates
"""
from django.conf import settings

def api_settings(request):
    """Adds API settings to template context"""
    return {
        'API_URL': settings.API_URL,
    }
