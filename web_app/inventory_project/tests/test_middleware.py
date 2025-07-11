"""
Tests for the middleware components of the inventory project
"""
from unittest import mock
from django.test import TestCase, RequestFactory
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.conf import settings

from inventory_project.middleware import RequestLoggerMiddleware
from inventory_project.error_middleware import ErrorHandlingMiddleware
from inventory_project.security_middleware import SecurityHeadersMiddleware, ClassificationHeaderMiddleware


class RequestLoggerMiddlewareTest(TestCase):
    """Test the request logger middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestLoggerMiddleware(get_response=lambda r: HttpResponse())
    
    @mock.patch('inventory_project.middleware.logger')
    def test_request_logging(self, mock_logger):
        """Test that requests are properly logged"""
        # Create a sample request
        request = self.factory.get('/test-path')
        request.user = mock.MagicMock(is_authenticated=True)
        
        # Process the request through middleware
        response = self.middleware(request)
        
        # Check that logger was called with expected arguments
        self.assertEqual(mock_logger.info.call_count, 2)
        
        # Check the first call (request start logging)
        args, _ = mock_logger.info.call_args_list[0]
        self.assertIn('Request started', args[0])
        self.assertIn('/test-path', args[0])
        
        # Check the second call (request complete logging)
        args, _ = mock_logger.info.call_args_list[1]
        self.assertIn('Request completed', args[0])
        self.assertIn('/test-path', args[0])
        
        # Check that response was returned correctly
        self.assertEqual(response.status_code, 200)


class ErrorHandlingMiddlewareTest(TestCase):
    """Test the error handling middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create middleware with a get_response that raises an exception
        def get_response(request):
            return HttpResponse("Success")
            
        self.middleware = ErrorHandlingMiddleware(get_response)
    
    def test_process_exception_ajax(self):
        """Test handling of exceptions for AJAX requests"""
        # Create a sample AJAX request
        request = self.factory.get('/test-path')
        request.headers = {'X-Requested-With': 'XMLHttpRequest'}
        request.user = mock.MagicMock()
        
        # Call the process_exception method with a test exception
        exception = ValueError("Test exception")
        response = self.middleware.process_exception(request, exception)
        
        # Check that a JSON response is returned for AJAX requests
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)
        
        # Parse the JSON response content
        content = response.json()
        self.assertEqual(content['status'], 'error')
        self.assertIn('message', content)
    
    @mock.patch('inventory_project.error_middleware.render_to_string')
    def test_process_exception_standard(self, mock_render):
        """Test handling of exceptions for standard requests"""
        # Set up the mock to return an HTML string
        mock_render.return_value = "<html>Error page</html>"
        
        # Create a sample standard request
        request = self.factory.get('/test-path')
        request.headers = {}
        request.user = mock.MagicMock()
        
        # Call the process_exception method with a test exception
        exception = ValueError("Test exception")
        response = self.middleware.process_exception(request, exception)
        
        # Check that an HTML response is returned for standard requests
        self.assertIsInstance(response, HttpResponseServerError)
        self.assertEqual(response.content.decode(), "<html>Error page</html>")
    
    @mock.patch('inventory_project.error_middleware.logger')
    def test_exception_logging(self, mock_logger):
        """Test that exceptions are properly logged"""
        # Create a sample request
        request = self.factory.get('/test-path')
        request.headers = {}
        request.user = mock.MagicMock()
        
        # Call the process_exception method with a test exception
        exception = ValueError("Test exception")
        self.middleware.process_exception(request, exception)
        
        # Check that logger was called with the exception
        mock_logger.error.assert_called_once()
        args, _ = mock_logger.error.call_args
        self.assertIn('Unhandled Exception', args[0])
        self.assertIn('ValueError', args[0])
        self.assertIn('/test-path', args[0])


class SecurityHeadersMiddlewareTest(TestCase):
    """Test the security headers middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(get_response=lambda r: HttpResponse())
    
    def test_security_headers_added(self):
        """Test that security headers are added to the response"""
        # Create a sample request
        request = self.factory.get('/equipment/detail/1')
        
        # Process the request through middleware
        response = self.middleware.process_response(request, HttpResponse())
        
        # Check that security headers are added
        self.assertIn('Content-Security-Policy', response)
        self.assertIn('Strict-Transport-Security', response)
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Referrer-Policy', response)
    
    def test_caching_headers_for_equipment(self):
        """Test that caching headers are added for equipment pages"""
        # Create a sample request for an equipment page
        request = self.factory.get('/equipment/detail/1')
        
        # Process the request through middleware
        response = self.middleware.process_response(request, HttpResponse())
        
        # Check that caching headers are added
        self.assertIn('Cache-Control', response)
        self.assertEqual(response['Cache-Control'], 'no-store, no-cache, must-revalidate, max-age=0')
        self.assertIn('Pragma', response)
        self.assertEqual(response['Pragma'], 'no-cache')
        self.assertIn('Expires', response)
        self.assertEqual(response['Expires'], '0')


class ClassificationHeaderMiddlewareTest(TestCase):
    """Test the classification headers middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ClassificationHeaderMiddleware(get_response=lambda r: HttpResponse())
    
    def test_default_classification(self):
        """Test that default classification header is added"""
        # Create a sample request
        request = self.factory.get('/equipment/list')
        request.META = {'REQUEST_TIME': '2023-07-10T10:00:00Z'}
        
        # Process the request through middleware
        response = self.middleware.process_response(request, HttpResponse())
        
        # Check that classification headers are added
        self.assertIn('X-Data-Classification', response)
        self.assertEqual(response['X-Data-Classification'], 'UNCLASSIFIED')
        self.assertIn('X-Access-Audited', response)
        self.assertEqual(response['X-Access-Audited'], 'true')
    
    def test_confidential_classification(self):
        """Test that confidential classification header is added"""
        # Create a sample request for a confidential equipment
        request = self.factory.get('/equipment/detail/1?classified=confidential')
        request.META = {'REQUEST_TIME': '2023-07-10T10:00:00Z'}
        
        # Process the request through middleware
        response = self.middleware.process_response(request, HttpResponse())
        
        # Check that classification headers are added
        self.assertIn('X-Data-Classification', response)
        self.assertEqual(response['X-Data-Classification'], 'CONFIDENTIAL')
    
    def test_secret_classification(self):
        """Test that secret classification header is added"""
        # Create a sample request for a secret equipment
        request = self.factory.get('/equipment/detail/1?classified=secret')
        request.META = {'REQUEST_TIME': '2023-07-10T10:00:00Z'}
        
        # Process the request through middleware
        response = self.middleware.process_response(request, HttpResponse())
        
        # Check that classification headers are added
        self.assertIn('X-Data-Classification', response)
        self.assertEqual(response['X-Data-Classification'], 'SECRET')
