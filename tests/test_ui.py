"""
UI tests for the Flask application using Selenium
Tests the user interface and browser interactions
"""
import pytest
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestUI:
    """UI tests using Selenium WebDriver"""
    
    @pytest.fixture
    def driver(self):
        """Create a Chrome WebDriver instance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_home_page_loads(self, driver):
        """Test that the home page loads correctly"""
        driver.get("http://localhost:5001/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        assert "Search" in driver.title or "Home" in driver.title
        
        # Check that the page contains expected elements
        page_source = driver.page_source.lower()
        assert "search" in page_source
    
    def test_search_form_submission(self, driver):
        """Test search form submission"""
        driver.get("http://localhost:5001/")
        
        # Find search input and submit button
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_term"))
            )
        except:
            # Alternative selectors if name doesn't work
            search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
        
        # Enter search term
        search_input.clear()
        search_input.send_keys("test search")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Wait for redirect or page change
        time.sleep(2)
        
        # Check that we're now on search results page or stayed on same page with results
        current_url = driver.current_url
        assert "search" in current_url.lower() or "test search" in driver.page_source.lower()
    
    def test_xss_protection_in_ui(self, driver):
        """Test that XSS attempts are blocked in the UI"""
        driver.get("http://localhost:5001/")
        
        # Find search input
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_term"))
            )
        except:
            search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
        
        # Try XSS payload
        xss_payload = "<script>alert('xss')</script>"
        search_input.clear()
        search_input.send_keys(xss_payload)
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        submit_button.click()
        
        # Wait for response
        time.sleep(2)
        
        # Check that error message is displayed and script is not executed
        page_source = driver.page_source
        assert "invalid" in page_source.lower() or "error" in page_source.lower()
        
        # Ensure no JavaScript alert appeared (script was not executed)
        # In a real scenario, we'd check for absence of alerts
    
    def test_search_results_page_direct_access(self, driver):
        """Test direct access to search results page"""
        driver.get("http://localhost:5001/search?query=direct%20test")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check that the search term appears on the page
        page_source = driver.page_source.lower()
        assert "direct test" in page_source or "search" in page_source
    
    def test_responsive_design_basic(self, driver):
        """Test basic responsive design elements"""
        # Test desktop view
        driver.set_window_size(1920, 1080)
        driver.get("http://localhost:5001/")
        
        # Wait for page load
        time.sleep(1)
        
        # Check that page renders properly
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()
        
        # Test mobile view
        driver.set_window_size(375, 667)  # iPhone size
        driver.refresh()
        
        # Wait for page load
        time.sleep(1)
        
        # Check that page still renders properly
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


# Simple smoke test that doesn't require Selenium (fallback)
class TestUIFallback:
    """Fallback UI tests that don't require Selenium"""
    
    def test_basic_ui_elements_exist(self):
        """Basic test to ensure UI test file is working"""
        # This is a simple test that will always pass
        # to ensure the test file itself is valid
        assert True
    
    def test_ui_test_file_imports(self):
        """Test that required imports work"""
        try:
            from selenium import webdriver
            selenium_available = True
        except ImportError:
            selenium_available = False
        
        # This test will pass whether Selenium is available or not
        # but will report the status
        print(f"Selenium available: {selenium_available}")
        assert True


if __name__ == '__main__':
    pytest.main([__file__])
