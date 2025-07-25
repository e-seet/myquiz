"""
Integration tests for the Flask application
Tests the application components working together
"""
import pytest
import sys
import os
import json

# Set environment variables before importing app
# os.environ['APP_USERNAME'] = 'testuser'
# os.environ['APP_PASSWORD'] = 'testpass'
# os.environ['SECRET_KEY'] = 'test-secret-key'

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app import app


class TestIntegration:
    """Integration tests for the Flask application"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['WTF_CSRF_ENABLED'] = False 
        
        with app.test_client() as client:
            yield client
    
    def test_complete_search_flow(self, client):
        """Test the complete search flow from home to results"""
        # Test GET request to home page
        response = client.get('/')
        assert response.status_code == 200
        assert b'Search Application' in response.data or b'home' in response.data.lower()
        
        # Test POST request with valid search
        response = client.post('/', data={'search_term': 'python programming'})
        assert response.status_code == 302  # Redirect to search results
        
        # Follow the redirect to search results
        response = client.get('/search?query=python%20programming')
        assert response.status_code == 200
        assert b'python programming' in response.data.lower()
    
    def test_security_validation_flow(self, client):
        """Test that security validation works end-to-end"""
        # Test XSS attempt
        response = client.post('/', data={'search_term': '<script>alert("xss")</script>'})
        assert response.status_code == 200  # Should stay on same page
        assert b'Invalid search term' in response.data
        
        # Test SQL injection attempt
        response = client.post('/', data={'search_term': "'; DROP TABLE users; --"})
        assert response.status_code == 200  # Should stay on same page
        assert b'Invalid search term' in response.data
    
    # def test_login_endpoint_integration(self, client):
    #     """Test the login endpoint with valid and invalid credentials"""
    #     # Import the app module to check environment variables
    #     from app.app import USERNAME, PASSWORD
        
    #     # Debug: Print the values to ensure they're set correctly
    #     print(f"USERNAME in app: {USERNAME}")
    #     print(f"PASSWORD in app: {PASSWORD}")
        
    #     # Test valid login - using the same credentials set in environment
    #     response = client.post('/login', 
    #                           data=json.dumps({'username': 'testuser', 'password': 'testpass'}),
    #                           content_type='application/json')
    #     print(f"Response status: {response.status_code}")
    #     print(f"Response data: {response.data}")
        
    #     assert response.status_code == 200
    #     data = json.loads(response.data)
    #     assert data['message'] == 'Login successful'
        
    #     # Test invalid login
    #     response = client.post('/login', 
    #                           data=json.dumps({'username': 'wrong', 'password': 'wrong'}),
    #                           content_type='application/json')
    #     assert response.status_code == 401
    #     data = json.loads(response.data)
    #     assert data['message'] == 'Invalid credentials'
    #     data = json.loads(response.data)
    #     assert data['message'] == 'Invalid credentials'
    
    def test_search_results_with_special_characters(self, client):
        """Test search results page handles various characters safely"""
        # Test with URL encoded characters
        response = client.get('/search?query=test%20search%20with%20spaces')
        assert response.status_code == 200
        assert b'test search with spaces' in response.data
        
        # Test with numbers
        response = client.get('/search?query=123456')
        assert response.status_code == 200
        assert b'123456' in response.data
    
    def test_error_handling(self, client):
        """Test error handling for edge cases"""
        # Test search results with empty query
        response = client.get('/search?query=')
        assert response.status_code == 200
        
        # Test search results with no query parameter
        response = client.get('/search')
        assert response.status_code == 200
    
    def test_flash_messages(self, client):
        """Test that flash messages work correctly"""
        # Test invalid search shows flash message
        response = client.post('/', data={'search_term': '<script>test</script>'})
        assert response.status_code == 200
        assert b'Invalid search term' in response.data


if __name__ == '__main__':
    pytest.main([__file__])
