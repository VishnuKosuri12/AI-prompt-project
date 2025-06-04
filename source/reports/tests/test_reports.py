import os
import sys
import pytest
import logging
import inspect
from shutil import rmtree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Return the name of the current function
myself = lambda: inspect.stack()[1][3]

# Establish the directories for logs and screen shots
# Remove the old stuff if it exists
LOG_DIR = "/tmp/tests/reports"
if os.path.exists(LOG_DIR):
    rmtree(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_DIR + "/tests_reports.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Service URLs
LOGIN_URL = "http://localhost:8001/login"
REPORTS_URL = "http://localhost:8008/reports"
MAIN_URL = "http://localhost:8003"

def is_chrome_available():
    """Check if Chrome and required dependencies are available"""
    try:
        # Check for local Chrome in project folder first
        project_root = "/home/jmh/projects/chemtrack"
        local_chrome_path = os.path.join(project_root, "chrome-linux64", "chrome")
        
        if os.path.exists(local_chrome_path) and os.access(local_chrome_path, os.X_OK):
            logger.info(f"Found local Chrome installation at: {local_chrome_path}")
            return True
        
        # Fallback to system Chrome binaries
        import subprocess
        chrome_binaries = ["google-chrome", "chrome", "chromium", "chromium-browser"]
        for binary in chrome_binaries:
            try:
                subprocess.run(f"which {binary}", shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info(f"Found Chrome binary: {binary}")
                return True
            except subprocess.CalledProcessError:
                continue
        
        # No Chrome binary found
        logger.warning("No Chrome browser binary found")
        return False
    except Exception as e:
        logger.warning(f"Error checking Chrome availability: {e}")
        return False

@pytest.fixture
def setup_driver():
    """Setup and teardown for Chrome WebDriver with the locally provided chromedriver"""
    driver = None
    
    # Skip Selenium tests if Chrome is not available
    if not is_chrome_available():
        logger.warning("Chrome browser not available - skipping Selenium test")
        pytest.skip("Chrome browser not available")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless (no UI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use local Chrome binary if available
        project_root = "/home/jmh/projects/chemtrack"
        local_chrome_path = os.path.join(project_root, "chrome-linux64", "chrome")
        if os.path.exists(local_chrome_path) and os.access(local_chrome_path, os.X_OK):
            logger.info(f"Using local Chrome binary: {local_chrome_path}")
            chrome_options.binary_location = local_chrome_path
        
        # Set absolute path to the user-provided chromedriver in the project root
        project_root = "/home/jmh/projects/chemtrack"
        chromedriver_path = os.path.join(project_root, "chromedriver-linux64", "chromedriver")
        
        logger.info(f"Using chromedriver at: {chromedriver_path}")
        
        # Check if chromedriver exists and is executable
        if not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver not found at {chromedriver_path}")
            pytest.skip("ChromeDriver not found")
            
        if not os.access(chromedriver_path, os.X_OK):
            logger.info(f"Making ChromeDriver executable: {chromedriver_path}")
            try:
                import subprocess
                subprocess.run(f"chmod +x {chromedriver_path}", shell=True, check=True)
            except Exception as e:
                logger.error(f"Failed to make ChromeDriver executable: {e}")
                pytest.skip("ChromeDriver not executable")
        
        # Create the driver
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to be available
        logger.info("Chrome WebDriver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {str(e)}")
        # Print the error details for debugging
        import traceback
        logger.error(traceback.format_exc())
        pytest.skip("Chrome driver setup failed, skipping test")
    
    # Yield the driver for the test
    yield driver
    
    # Cleanup after test
    if driver:
        driver.quit()

class TestReportsIntegration:
    """Integration tests for the reports module"""  

    def test_reports_page_access_technician(self, setup_driver):
        """Test that technician role can login and navigate to reports page"""
        logger.info("Testing technician role access to reports page")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        
        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit - using sally who has technician role
            logger.info("Logging in with user sally (technician role)")
            username_field.send_keys("sally")
            password_field.send_keys("sally")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Take a screenshot after login
            driver.save_screenshot(f"{LOG_DIR}/{myself()}_after_login.png")
            
            # Now navigate to reports page
            logger.info(f"Navigating to reports page: {REPORTS_URL}")
            driver.get(REPORTS_URL)
            
            # Take a screenshot of reports page
            driver.save_screenshot(f"{LOG_DIR}/{myself()}_reports_page.png")
            
            # Check for reports page title and content
            assert "ChemTrack - Reporting" in driver.title
            assert "Reporting" in driver.page_source
            assert "Welcome to the Reporting Module" in driver.page_source
            
            # Check that we have the shared header
            header = driver.find_element(By.CSS_SELECTOR, ".header")
            assert header is not None, "Header not found on reports page"
            assert "ChemTrack" in header.text, "ChemTrack not found in header"
            
            # Check that we have the shared navigation
            nav = driver.find_element(By.CSS_SELECTOR, ".nav-sidebar")
            assert nav is not None, "Navigation not found on reports page"
            assert "Home" in nav.text, "Home link not found in navigation"
            assert "Search" in nav.text, "Search link not found in navigation"
            assert "Reports" in nav.text, "Reports link not found in navigation"
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_reports_page_without_login(self, setup_driver):
        """Test that navigating to reports page without login redirects to login page"""
        logger.info("Testing reports page access without login")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        
        try:
            # Navigate directly to reports page without login
            logger.info(f"Attempting to navigate to reports page without login: {REPORTS_URL}")
            driver.get(REPORTS_URL)
            
            # Take a screenshot after redirect
            driver.save_screenshot(f"{LOG_DIR}/{myself()}_after_redirect.png")
            
            # Check we were redirected to login
            current_url = driver.current_url
            logger.info(f"Current URL after trying to access reports without login: {current_url}")
            
            # Check that we are redirected to login page
            assert "8001" in current_url, "Not redirected to login page when accessing reports without login"
            assert "login" in current_url.lower(), "Not redirected to login page when accessing reports without login"
            assert "username" in driver.page_source.lower(), "Login form not found after redirect"
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise

if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main(["-v", __file__])
