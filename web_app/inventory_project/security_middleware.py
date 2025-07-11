"""
Security middleware for the inventory project
Implements military-grade security headers and content security policy
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        # Restricts sources of content that can be loaded
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://code.jquery.com 'unsafe-inline'; "
            "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com 'unsafe-inline'; "
            "font-src 'self' https://cdnjs.cloudflare.com https://cdn.cloudflare.com https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "img-src 'self' data: https://www.transparenttextures.com https://*.transparenttextures.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )
        
        # HTTP Strict Transport Security
        # Force browsers to use HTTPS for a specified period
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # X-Content-Type-Options
        # Prevents browsers from MIME-sniffing a response from the declared content-type
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        # Prevents content from being loaded in an iframe on other sites
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        # Enables browser's XSS filtering
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        # Controls how much referrer information is included with requests
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Cache-Control
        # Prevents caching of sensitive data
        if request.path.startswith('/equipment/') and not request.path.endswith(('.css', '.js')):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Log security headers for auditing purposes in debug mode
        if hasattr(request, 'is_secure') and not request.is_secure():
            logger.warning(f"Insecure request to {request.path} - security headers may not provide full protection")
            
        return response


class ClassificationHeaderMiddleware(MiddlewareMixin):
    """Middleware to add classification headers for military data"""
    
    def process_response(self, request, response):
        # Default classification level
        classification = "UNCLASSIFIED"
        
        # Check if this is an equipment detail page with classification
        if request.path.startswith('/equipment/detail/'):
            # In a real system, you would get this from the equipment data
            # For now we'll set based on URL
            if 'classified=confidential' in request.GET:
                classification = "CONFIDENTIAL"
            elif 'classified=secret' in request.GET:
                classification = "SECRET"
        
        # Add classification header
        response['X-Data-Classification'] = classification
        
        # Add metadata for audit trail
        response['X-Access-Audited'] = 'true'
        response['X-Access-Timestamp'] = request.META.get('REQUEST_TIME', '')
        
        return response
