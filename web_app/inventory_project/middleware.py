"""
Custom middleware for the inventory project
"""
import logging
import time

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware:
    """Middleware to log all requests to the application"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Log request details
        logger.info(f"Request started: {request.method} {request.path} - User: {request.user}")
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Request completed: {request.method} {request.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Return response
        return response
