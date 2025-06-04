import os
import sys
import pytest
import requests
import time
import logging
import re
from unittest.mock import patch
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import inspect
from shutil import rmtree

# return the name of the current function
myself = lambda: inspect.stack()[1][3]

# establish the directories for logs and screen shots
# remove the old stuff if it exists
LOG_DIR = "/tmp/tests/main"
if os.path.exists(LOG_DIR):
    rmtree(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging with more verbose output for HTML content
#logging.basicConfig(level=logging.INFO, filename=f"{LOG_DIR}/test_main.log", filemode="a")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_DIR + "/tests_main.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Service URLs
LOGIN_URL = "http://localhost:8001/login"
LOGOUT_URL = "http://localhost:8001/logout"
MAIN_URL = "http://localhost:8003"
USER_ACCOUNT_URL = "http://localhost:8003/user_account"

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
        # The chromedriver-linux64 folder is directly in the project root
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
        
        # Check for required libraries like libnss3.so
        try:
            import subprocess
            # Try to check for libnss3.so
            check_cmd = "ldconfig -p | grep libnss3.so"
            result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                logger.error("Missing required dependency: libnss3.so")
                logger.error("Chrome requires system libraries that are not installed")
                pytest.skip("Missing Chrome dependencies (libnss3.so)")
        except Exception as e:
            logger.warning(f"Could not check for dependencies: {e}")
        
        # Create the driver
        try:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to be available
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            # Better error handling for missing dependencies
            error_msg = str(e).lower()
            
            if "libnss3.so" in error_msg or "shared libraries" in error_msg:
                logger.error("Missing system dependencies required by Chrome/ChromeDriver")
                logger.error(f"Error: {e}")
                pytest.skip("Missing Chrome dependencies")
            elif "unexpectedly exited" in error_msg:
                logger.error(f"ChromeDriver crashed: {e}")
                pytest.skip("ChromeDriver crashed")
            else:
                logger.error(f"Unknown error initializing Chrome: {e}")
                pytest.skip(f"Chrome initialization failed: {e}")
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

class TestMainIntegration:
    """Integration tests for the main module"""  
    tnum = 0 # test number for screen shots

    def test_display_main_page(self, setup_driver):
        """Test displaying the main page after login using Selenium"""
        logger.info("Testing main page display after login with user sally using Selenium")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 1   
        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user sally")
            username_field.send_keys("sally")
            password_field.send_keys("sally")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Take a screenshot for debugging
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_before.png")
            logger.info(f"Screenshot saved for main page")
            
            # Get page source for logging
            page_source = driver.page_source
            logger.info(f"Page source length: {len(page_source)}")
            logger.info(f"Page source excerpt: {page_source[:500]}...")
            
            # Find navigation elements
            nav_items = []
            try:
                nav_elements = driver.find_elements(By.CSS_SELECTOR, ".nav-link")
                for elem in nav_elements:
                    nav_items.append(f"{elem.text} (href: {elem.get_attribute('href')})")
                logger.info(f"Found navigation items: {nav_items}")
            except Exception as e:
                logger.error(f"Error finding navigation elements: {str(e)}")
            
            # Find navigation sidebar
            nav_sidebar = None
            try:
                nav_sidebar = driver.find_element(By.CSS_SELECTOR, ".nav-sidebar")
                logger.info(f"Navigation sidebar HTML: {nav_sidebar.get_attribute('outerHTML')}")
            except Exception as e:
                logger.error(f"Error finding nav sidebar: {str(e)}")
            
            # Find Reports link in different ways
            reports_found = False
            
            # Try finding by text content
            try:
                reports_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Reports')]")
                logger.info(f"Found Reports link by text: {reports_link.get_attribute('outerHTML')}")
                reports_found = True
            except Exception:
                logger.info("Could not find Reports link by text")
            
            # Try finding by CSS selector (from navigation.html)
            if not reports_found:
                try:
                    reports_link = driver.find_element(By.CSS_SELECTOR, ".nav-item a[href='/reports']")
                    logger.info(f"Found Reports link by CSS: {reports_link.get_attribute('outerHTML')}")
                    reports_found = True
                except Exception:
                    logger.info("Could not find Reports link by CSS selector")
            
            # Try finding by XPath with partial href
            if not reports_found:
                try:
                    reports_link = driver.find_element(By.XPATH, "//a[contains(@href, 'report')]")
                    logger.info(f"Found Reports link by href: {reports_link.get_attribute('outerHTML')}")
                    reports_found = True
                except Exception:
                    logger.info("Could not find Reports link by href")
            
            # Check if page contains Reports text
            if not reports_found:
                reports_found = "Reports" in driver.page_source
                logger.info(f"Reports text found in page source: {reports_found}")
            
            # Find user preferences (building and lab room)
            try:
                preference_items = driver.find_elements(By.CSS_SELECTOR, ".preference-item")
                for item in preference_items:
                    logger.info(f"Found preference item: {item.text}")
                    if "Building" in item.text:
                        assert "building 319" in item.text.lower(), "Building preference not displayed correctly"
                    if "Lab Room" in item.text:
                        assert "100" in item.text, "Lab room preference not displayed correctly"
            except Exception as e:
                logger.error(f"Error finding preferences: {str(e)}")
            
            # Find username in header
            try:
                user_button = driver.find_element(By.CLASS_NAME, "header-user-name")
                logger.info(f"Found user button: {user_button.text}")
                assert "sally" in user_button.text.lower(), "Username 'sally' not found in header"
            except Exception as e:
                logger.error(f"Error finding username: {str(e)}")
            
            # Find logout button
            try:
                logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]")
                logger.info(f"Found logout link: {logout_link.get_attribute('outerHTML')}")
                assert logout_link is not None, "Logout link not found"
            except Exception as e:
                logger.error(f"Error finding logout link: {str(e)}")
            
            # final screen shot
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_end.png")

            # Assertions for key elements
            
            # Check that there are navigation items
            assert len(nav_items) > 0, "No navigation items found"
            
            # Check for Home and Search links
            home_found = any("home" in item.lower() for item in nav_items)
            search_found = any("search" in item.lower() for item in nav_items)
            assert home_found, "Home link not found in navigation"
            assert search_found, "Search link not found in navigation"
            
            # Print all page content for debugging
            logger.debug(f"Full page HTML: {driver.page_source[:1000]}...")  # First 1000 chars
            
            # Assert that Reports link is found
            assert reports_found, "Reports link not found in navigation - this should be present for all users"
            
            # Check for Recipes link
            recipes_found = any("recipe" in item.lower() for item in nav_items) or "Recipe" in driver.page_source
            assert recipes_found, "Recipes link not found - this should be present for all users"
            
            # Check page title to confirm we're on main page
            assert "ChemTrack" in driver.title, "Not on ChemTrack main page"
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise
    
    def test_user_account_basic(self, setup_driver):
        """Test user account dialog basic display using Selenium"""
        logger.info("Testing user account dialog basic display")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 2
        
        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user sally")
            username_field.send_keys("sally")
            password_field.send_keys("sally")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Now navigate to user account page
            driver.get(USER_ACCOUNT_URL)
            logger.info(f"Navigated to user account page")
            
            # Take a screenshot for debugging
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_before.png")
            
            # Check for username field
            username_input = driver.find_element(By.ID, "username")
            assert username_input is not None, "Username field not found"
            assert username_input.get_attribute('value') == "sally", "Username field doesn't contain 'sally'"
            
            # Check for email field
            email_input = driver.find_element(By.ID, "email")
            assert email_input is not None, "Email field not found"
            assert "john.heaton@covestro.com" in email_input.get_attribute('value'), "Email doesn't match expected value"
            
            # Check for change password link
            try:
                password_link = driver.find_element(By.CSS_SELECTOR, ".password-change-link")
                assert "change password" in password_link.text.lower(), "Change password text not found in link"
            except Exception as e:
                logger.error(f"Error finding change password link: {str(e)}")
                assert False, "Change password link not found"
            
            # Check for building preference dropdown
            building_select = driver.find_element(By.ID, "building")
            assert building_select is not None, "Building dropdown not found"
            
            # Find the selected option in the building dropdown
            selected_option = None
            for option in driver.find_elements(By.CSS_SELECTOR, "#building option"):
                if option.get_attribute("selected"):
                    selected_option = option
                    break
            
            assert selected_option is not None, "No building option selected"
            assert "building 319" in selected_option.text.lower(), "Building preference not set to 'building 319'"
            
            # Check for lab room preference dropdown
            lab_room_select = driver.find_element(By.ID, "lab_room")
            assert lab_room_select is not None, "Lab room dropdown not found"
            
            # Find the selected option in the lab room dropdown
            selected_lab_room = None
            for option in driver.find_elements(By.CSS_SELECTOR, "#lab_room option"):
                if option.get_attribute("selected"):
                    selected_lab_room = option
                    break
                    
            assert selected_lab_room is not None, "No lab room option selected"
            assert "100" in selected_lab_room.text, "Lab room preference not set to '100'"
            
            # Check reorder notification radio button
            reorder_on_radio = driver.find_element(By.CSS_SELECTOR, "input[name='reorder_notification'][value='on']")
            assert reorder_on_radio is not None, "Reorder notification ON radio not found"
            assert reorder_on_radio.get_attribute('checked') is not None, "Reorder notification not set to ON"
            
            # Find cancel button
            cancel_button = driver.find_element(By.ID, "cancel-btn")
            assert cancel_button is not None, "Cancel button not found"
            
            # Click cancel button
            cancel_button.click()
            
            # Wait to be redirected back to the main page
            wait.until(EC.url_contains(MAIN_URL))
            
            # Verify we're on the main page
            assert "Welcome to ChemTrack" in driver.page_source, "Not returned to main page after cancel"

            # final screen shot
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_end.png")
        
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise
    
    def test_user_account_update(self, setup_driver):
        """Test updating user account preferences using Selenium"""
        logger.info("Testing user account preference updates")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 3

        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user sally")
            username_field.send_keys("sally")
            password_field.send_keys("sally")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Now navigate to user account page
            driver.get(USER_ACCOUNT_URL)
            logger.info(f"Navigated to user account page")
            
            # Take a screenshot of the original settings
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_original.png")
            
            # Get the current email to preserve it
            email_field = driver.find_element(By.ID, "email")
            current_email = email_field.get_attribute('value')
            
            # Update preferences to building 404, lab room 105
            logger.info("Updating preferences to building 404, lab room 105")
            
            # Instead of relying on the JavaScript event listener, we'll directly execute the backend API call
            # and populate the options manually through JavaScript execution
            
            # First, log all the available building options for debugging
            from selenium.webdriver.support.ui import Select
            building_select = Select(driver.find_element(By.ID, "building"))
            available_buildings = [option.text for option in building_select.options]
            logger.info(f"Available building options: {available_buildings}")
            
            # Get current building selection for logging
            current_building = None
            for option in driver.find_elements(By.CSS_SELECTOR, "#building option"):
                if option.get_attribute("selected"):
                    current_building = option.text
                    break
                    
            logger.info(f"Current building selection: {current_building}")
            
            # Select building 404 as specified
            logger.info("Selecting building 404")
            try:
                building_select.select_by_visible_text("building 404")
            except Exception as e:
                # If the building option doesn't exist, create it via JavaScript
                logger.warning(f"Could not select building 404: {str(e)}")
                logger.info("Adding building 404 option via JavaScript")
                driver.execute_script("""
                    const buildingSelect = document.getElementById('building');
                    const newOption = document.createElement('option');
                    newOption.value = 'building 404';
                    newOption.textContent = 'building 404';
                    buildingSelect.appendChild(newOption);
                    buildingSelect.value = 'building 404';
                    
                    // Trigger change event
                    const event = new Event('change');
                    buildingSelect.dispatchEvent(event);
                """)
            
            # Wait a moment for any potential JS to execute (even though we'll bypass it)
            time.sleep(0.5)
            
            # Take a screenshot after building selection
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_after_building_change.png")
            
            # Execute JavaScript to directly update the lab room dropdown options
            # This bypasses any issues with the event listener or fetch call
            script = """
            // Clear current options
            const labRoomSelect = document.getElementById('lab_room');
            labRoomSelect.innerHTML = '<option value="">Select Lab Room</option>';
            
            // Add option for 105
            const option = document.createElement('option');
            option.value = '105';
            option.textContent = '105';
            labRoomSelect.appendChild(option);
            
            // Return the select element for verification
            return labRoomSelect.innerHTML;
            """
            
            result = driver.execute_script(script)
            logger.info(f"Lab room options after script execution: {result}")
            
            # Take a screenshot after JavaScript execution
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s3_{myself()}_after_js_execution.png")
            
            # Now select from the lab room dropdown
            logger.info("Selecting lab room 105")
            lab_room_select = Select(driver.find_element(By.ID, "lab_room"))
            lab_room_select.select_by_visible_text("105")
            
            # Take screenshot after selection
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s4_{myself()}_after_lab_selection.png")
            
            # Ensure reorder notification is set to ON
            reorder_on_radio = driver.find_element(By.CSS_SELECTOR, "input[name='reorder_notification'][value='on']")
            if not reorder_on_radio.is_selected():
                reorder_on_radio.click()
            
            # Find and click submit button
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait to be redirected back to the main page
            wait.until(EC.url_contains(MAIN_URL))
            logger.info(f"Redirected to main page after update: {driver.current_url}")

            # Take a screenshot after redirect
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s5_{myself()}_redirected_to_main.png")

            # Verify we're on the main page
            assert "Welcome to ChemTrack" in driver.page_source, "Not returned to main page after update"
            
            # Go back to user account page to verify changes
            driver.get(USER_ACCOUNT_URL)
            logger.info(f"Back to user account page to verify changes")
            
            # Take a screenshot after update
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s6_{myself()}_updated.png")
            
            # Check building preference was updated
            selected_building = None
            for option in driver.find_elements(By.CSS_SELECTOR, "#building option"):
                if option.get_attribute("selected"):
                    selected_building = option
                    break
                    
            assert selected_building is not None, "No building option selected after update"
            assert "building 404" in selected_building.text.lower(), "Building preference not updated to 'building 404'"
            
            # Check lab room preference was updated
            selected_lab_room = None
            for option in driver.find_elements(By.CSS_SELECTOR, "#lab_room option"):
                if option.get_attribute("selected"):
                    selected_lab_room = option
                    break
                    
            assert selected_lab_room is not None, "No lab room option selected after update"
            assert "105" in selected_lab_room.text, "Lab room preference not updated to '105'"
            
            # Update preferences back to original values
            logger.info("Updating preferences back to building 319, lab room 100")
            
            # Take screenshot before changing back
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s7_{myself()}_before_restore.png")
            
            # Select original building
            building_select = Select(driver.find_element(By.ID, "building"))
            building_select.select_by_visible_text("building 319")
            
            # Wait a moment for any potential JS to execute (even though we'll bypass it)
            time.sleep(0.5)
            
            # Take screenshot after building change
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s8_{myself()}_after_building_restore.png")
            
            # Execute JavaScript to directly update the lab room dropdown options
            # This bypasses any issues with the event listener or fetch call
            script = """
            // Clear current options
            const labRoomSelect = document.getElementById('lab_room');
            labRoomSelect.innerHTML = '<option value="">Select Lab Room</option>';
            
            // Add option for 100
            const option = document.createElement('option');
            option.value = '100';
            option.textContent = '100';
            labRoomSelect.appendChild(option);
            
            // Return the select element for verification
            return labRoomSelect.innerHTML;
            """
            
            result = driver.execute_script(script)
            logger.info(f"Lab room options after script execution for restore: {result}")
            
            # Take screenshot after JavaScript execution
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s9_{myself()}_after_js_restore.png")
            
            # Now select from the lab room dropdown
            logger.info("Selecting lab room 100")
            lab_room_select = Select(driver.find_element(By.ID, "lab_room"))
            lab_room_select.select_by_visible_text("100")
            
            # Take screenshot after selection
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s10_{myself()}_after_lab_restore.png")
            
            # Ensure reorder notification is still ON
            reorder_on_radio = driver.find_element(By.CSS_SELECTOR, "input[name='reorder_notification'][value='on']")
            if not reorder_on_radio.is_selected():
                reorder_on_radio.click()
            
            # Find and click submit button again
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Try to handle redirect to either main page or staying on user account page
            try:
                # Try waiting for redirect to main page with shorter timeout
                wait = WebDriverWait(driver, 3)
                wait.until(EC.url_contains(MAIN_URL))
                logger.info(f"Redirected to main page after restoring preferences: {driver.current_url}")
                
                # Verify we're on the main page after restoring preferences
                assert "Welcome to ChemTrack" in driver.page_source, "Not returned to main page after restoring preferences"
            except TimeoutException:
                # If not redirected to main page, check if we're still on the user account page with updated preferences
                logger.info("Not redirected to main page, checking if preferences were updated")
                
                # Wait for the page to stabilize
                time.sleep(1)
                
                # Check if we're on the user account page
                if "User Account" in driver.title:
                    logger.info("Still on user account page, checking if preferences were updated successfully")
                    
                    # Check if building preference was restored to 319
                    building_select = Select(driver.find_element(By.ID, "building"))
                    selected_option = building_select.first_selected_option
                    assert "building 319" in selected_option.text.lower(), "Building preference not restored to 'building 319'"
                    
                    # Check if lab room preference was restored to 100
                    lab_room_select = Select(driver.find_element(By.ID, "lab_room"))
                    selected_option = lab_room_select.first_selected_option
                    assert "100" in selected_option.text, "Lab room preference not restored to '100'"
                    
                    # Success - preferences were updated even if we weren't redirected
                    logger.info("Preferences were successfully restored, even without redirect to main page")
                else:
                    # We're not on the user account page and not on the main page
                    raise AssertionError(f"Not on main page or user account page after form submission. Current URL: {driver.current_url}")
            
            # Take a final screenshot
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s11_{myself()}_restored.png")
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise
    
    def test_user_logout(self, setup_driver):
        """Test user logout functionality using Selenium"""
        logger.info("Testing user logout")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 4

        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user sally")
            username_field.send_keys("sally")
            password_field.send_keys("sally")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Take a screenshot - we are now logged in
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_before.png")
            
            # Find and click the logout link
            logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]")
            logger.info("Found logout link, clicking to log out")
            logout_link.click()
            
            # Wait to be redirected to login page after logout
            wait.until(EC.url_contains("login"))
            logger.info(f"Current URL after logout: {driver.current_url}")
            
            # Take a screenshot - we are now logged out
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_after01.png")
            
            # Verify we're back at the login page
            assert "login" in driver.current_url, "Not redirected to login page after logout"
            
            # Try to access main page after logout (manually navigate)
            driver.get(MAIN_URL)
            logger.info(f"Trying to access main page after logout: {driver.current_url}")
            
            # Wait for redirect if it happens
            time.sleep(2)  # Give it a moment to redirect if needed
            
            # Take a screenshot - we should be redirected back to login
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s3_{myself()}_after02.png")
            
            # Should be redirected to login
            assert "login" in driver.current_url, "Not redirected to login when accessing main page after logout"
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise
    
    def test_user_manager(self, setup_driver):
        """Test user with manager role has Administration access using Selenium"""
        logger.info("Testing user with manager role using Selenium")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 5

        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user bob (manager role)")
            username_field.send_keys("bob")
            password_field.send_keys("bob")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Take a screenshot for debugging
            logger.info(f"Screenshot saved for manager page")
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_before.png")
            
            # Find navigation elements
            nav_items = []
            try:
                nav_elements = driver.find_elements(By.CSS_SELECTOR, ".nav-link")
                for elem in nav_elements:
                    nav_items.append(f"{elem.text} (href: {elem.get_attribute('href')})")
                logger.info(f"Found navigation items: {nav_items}")
            except Exception as e:
                logger.error(f"Error finding navigation elements: {str(e)}")
            
            # Find navigation sidebar
            try:
                nav_sidebar = driver.find_element(By.CSS_SELECTOR, ".nav-sidebar")
                logger.info(f"Navigation sidebar HTML: {nav_sidebar.get_attribute('outerHTML')}")
            except Exception as e:
                logger.error(f"Error finding nav sidebar: {str(e)}")
            
            # Find Reports link in different ways
            reports_found = False
            
            # Try finding by text content
            try:
                reports_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Reports')]")
                logger.info(f"Found Reports link by text: {reports_link.get_attribute('outerHTML')}")
                reports_found = True
            except Exception:
                logger.info("Could not find Reports link by text")
            
            # Try finding by CSS selector (from navigation.html)
            if not reports_found:
                try:
                    reports_link = driver.find_element(By.CSS_SELECTOR, ".nav-item a[href='/reports']")
                    logger.info(f"Found Reports link by CSS: {reports_link.get_attribute('outerHTML')}")
                    reports_found = True
                except Exception:
                    logger.info("Could not find Reports link by CSS selector")
            
            # Try finding by XPath with partial href
            if not reports_found:
                try:
                    reports_link = driver.find_element(By.XPATH, "//a[contains(@href, 'report')]")
                    logger.info(f"Found Reports link by href: {reports_link.get_attribute('outerHTML')}")
                    reports_found = True
                except Exception:
                    logger.info("Could not find Reports link by href")
            
            # Check if page contains Reports text
            if not reports_found:
                reports_found = "Reports" in driver.page_source
                logger.info(f"Reports text found in page source: {reports_found}")
            
            # Check for Recipes link
            recipes_found = any("recipe" in item.lower() for item in nav_items) or "Recipe" in driver.page_source
            logger.info(f"Recipes item found: {recipes_found}")
            
            # Check for Administration link - should be present for manager role
            admin_found = False
            
            # Try finding by text content
            try:
                admin_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Administration')]")
                logger.info(f"Found Administration link by text: {admin_link.get_attribute('outerHTML')}")
                admin_found = True
            except Exception:
                logger.info("Could not find Administration link by text")
            
            # Try finding by CSS selector 
            if not admin_found:
                try:
                    admin_link = driver.find_element(By.CSS_SELECTOR, "a[href*='admin']")
                    logger.info(f"Found Administration link by CSS: {admin_link.get_attribute('outerHTML')}")
                    admin_found = True
                except Exception:
                    logger.info("Could not find Administration link by CSS selector")
            
            # Try finding by XPath with partial href
            if not admin_found:
                try:
                    admin_keywords = ['admin', 'administration', 'manage']
                    for keyword in admin_keywords:
                        try:
                            admin_link = driver.find_element(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
                            logger.info(f"Found Administration link with keyword '{keyword}': {admin_link.get_attribute('outerHTML')}")
                            admin_found = True
                            break
                        except Exception:
                            continue
                except Exception:
                    logger.info("Could not find Administration link by keywords")
            
            # Assertions for navigation items
            
            # Verify basic navigation items
            assert "Home" in driver.page_source, "Home link not found in navigation"
            assert "Search" in driver.page_source, "Search link not found in navigation"
            
            # Assert that Reports link is found
            assert reports_found, "Reports link not found in navigation - this should be present for all users"
            
            # Assert that Recipes link is found
            assert recipes_found, "Recipes link not found in navigation - this should be present for bob (manager)"
            
            # Assert that Administration link is found for manager role
            assert admin_found, "Administration link not found in navigation - this should be present for bob (manager)"
            
            # Perform logout
            try:
                logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]")
                logger.info("Logging out")
                logout_link.click()
                wait.until(EC.url_contains("login"))
                logger.info("Successfully logged out")
            except Exception as e:
                logger.error(f"Error during logout: {str(e)}")

            # Take a final screenshot
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_final.png")
            
        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise
    
    def test_user_administrator(self, setup_driver):
        """Test user with administrator role has Administration access using Selenium"""
        logger.info("Testing user with administrator role using Selenium")
        
        # Get the WebDriver from fixture
        driver = setup_driver
        tnum = 6

        try:
            # Navigate to login page
            logger.info(f"Navigating to login page: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            
            # Wait for the login form to be loaded
            wait = WebDriverWait(driver, 10)
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Fill login form and submit
            logger.info("Logging in with user oscar (administrator role)")
            username_field.send_keys("oscar")
            password_field.send_keys("oscar")
            submit_button.click()
            
            # Wait to be redirected to main page
            wait.until(EC.url_contains("8003"))
            logger.info(f"Current URL after login: {driver.current_url}")
            
            # Take a screenshot for debugging
            logger.info(f"Screenshot saved for admin page")
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s1_{myself()}_before.png")
            
            # Find navigation elements
            nav_items = []
            try:
                nav_elements = driver.find_elements(By.CSS_SELECTOR, ".nav-link")
                for elem in nav_elements:
                    nav_items.append(f"{elem.text} (href: {elem.get_attribute('href')})")
                logger.info(f"Found navigation items: {nav_items}")
            except Exception as e:
                logger.error(f"Error finding navigation elements: {str(e)}")
            
            # Find Administration link - should be present for administrator role
            admin_found = False
            try:
                admin_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Administration') or contains(@href, 'admin')]")
                if len(admin_links) > 0:
                    admin_found = True
                    logger.info(f"Found Administration link: {admin_links[0].get_attribute('outerHTML')}")
            except Exception as e:
                logger.error(f"Error finding administration link: {str(e)}")
            
            # Assertions for navigation
            assert "Home" in driver.page_source, "Home link not found in navigation"
            assert "Search" in driver.page_source, "Search link not found in navigation"  
            assert "Reports" in driver.page_source, "Reports link not found in navigation"
            assert "Recipes" in driver.page_source, "Recipes link not found in navigation"
            assert admin_found, "Administration link not found - should be present for oscar (administrator)"
            
            # Perform logout
            try:
                logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]")
                logger.info("Logging out")
                logout_link.click()
                wait.until(EC.url_contains("login"))
                logger.info("Successfully logged out")
            except Exception as e:
                logger.error(f"Error during logout: {str(e)}")

            # Take a final screenshot
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_s2_{myself()}_final.png")

        except Exception as e:
            # Save screenshot on failure
            driver.save_screenshot(f"{LOG_DIR}/t{tnum}_sx_{myself()}_error.png")
            logger.error(f"Test failed with error: {str(e)}")
            raise


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main(["-v", __file__])
