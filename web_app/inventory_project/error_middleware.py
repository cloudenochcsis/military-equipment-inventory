"""
Error handling middleware for the inventory project
"""
import logging
import traceback
from django.http import JsonResponse, HttpResponseServerError
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Middleware to catch, log and handle unhandled exceptions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Process exceptions raised during request processing"""
        # Get the full traceback
        trace = traceback.format_exc()
        
        # Log the exception with traceback
        logger.error(
            f"Unhandled Exception: {exception.__class__.__name__}: {str(exception)}\n"
            f"Path: {request.path}\n"
            f"User: {request.user}\n"
            f"{trace}"
        )
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Server error occurred',
                'detail': str(exception) if settings.DEBUG else 'Please contact support'
            }, status=500)
        
        # For regular requests, render an error page
        try:
            context = {
                'exception_type': exception.__class__.__name__,
                'exception_value': str(exception),
                'exception_trace': trace if settings.DEBUG else None,
                'request': request
            }
            
            error_html = render_to_string('500.html', context)
            return HttpResponseServerError(error_html)
        except Exception as render_exception:
            # If the error template rendering fails, provide a simple error response
            logger.error(f"Error rendering 500 template: {render_exception}")
            return HttpResponseServerError(
                "<h1>Server Error (500)</h1>"
                "<p>A server error occurred. Please try again later.</p>"
                f"<p>Error type: {exception.__class__.__name__}</p>"
            )
