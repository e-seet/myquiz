"""
Unit tests for the Flask application
Tests individual functions and components in isolation
"""
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app import app, validate_search_input


class TestSearchValidation:
    """Test the search input validation function"""
    
    def test_valid_input(self):
        """Test that valid inputs pass validation"""
        assert validate_search_input("hello world") == True
        assert validate_search_input("test123") == True
        assert validate_search_input("python programming") == True
    
    def test_empty_input(self):
        """Test that empty inputs fail validation"""
        assert validate_search_input("") == False
        assert validate_search_input("   ") == False
        assert validate_search_input(None) == False
    
    def test_xss_patterns(self):
        """Test that XSS patterns are blocked"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onclick=alert('xss')",
            "<iframe src='malicious'></iframe>",
            "vbscript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        for xss_input in xss_inputs:
            assert validate_search_input(xss_input) == False, f"XSS input should be blocked: {xss_input}"
    
    def test_sql_injection_patterns(self):
        """Test that SQL injection patterns are blocked"""
        sql_inputs = [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM passwords",
            "' OR '1'='1",
            "'; DELETE FROM users; --",
            "'; INSERT INTO admin VALUES('hacker'); --",
            "exec xp_cmdshell('dir')"
        ]
        for sql_input in sql_inputs:
            assert validate_search_input(sql_input) == False, f"SQL injection should be blocked: {sql_input}"
    
    def test_suspicious_characters(self):
        """Test that suspicious characters are blocked"""
        suspicious_inputs = [
            "test<script>",
            "hello>world",
            'test"quotes',
            "test'quotes",
            "test;command",
            "test(function)",
            "test{object}",
        ]
        for suspicious_input in suspicious_inputs:
            assert validate_search_input(suspicious_input) == False, f"Suspicious characters should be blocked: {suspicious_input}"


class TestFlaskApp:
    """Test Flask application functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False 
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_client() as client:
            yield client
    
    def test_home_page_get(self, client):
        """Test that home page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Search Application' in response.data
    
    def test_valid_search_submission(self, client):
        """Test valid search form submission"""
        response = client.post('/', data={'search_term': 'valid search'})
        assert response.status_code == 302  # Redirect to search results
    
    def test_invalid_search_submission(self, client):
        """Test invalid search form submission"""
        response = client.post('/', data={'search_term': '<script>alert("xss")</script>'})
        assert response.status_code == 200  # Stay on same page
        assert b'Invalid search term' in response.data
    
    def test_search_results_page(self, client):
        """Test search results page"""
        response = client.get('/search?query=test')
        assert response.status_code == 200
        assert b'Search Results' in response.data
        assert b'test' in response.data


if __name__ == '__main__':
    pytest.main([__file__])
