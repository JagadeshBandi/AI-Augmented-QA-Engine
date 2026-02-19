"""
Advanced Login Test Suite - Entry Point
Demonstrates AI-augmented login testing with enterprise features
"""

import pytest
import asyncio
from playwright.sync_api import sync_playwright, Page
from src.pages.login_page import LoginPage


@pytest.mark.asyncio
async def test_ai_recovery_demo():
    """
    Advanced AI healing demonstration with comprehensive login testing
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        try:
            # Initialize advanced login page
            login_page = LoginPage(page)
            
            # Navigate to login page
            await login_page.navigate_to_login("https://example.com/login")
            
            # Perform advanced login with AI healing
            result = await login_page.smart_login(
                username="test@example.com",
                password="SecurePass123!",
                remember_me=False,
                use_ai_healing=True
            )
            
            # Validate results
            print(f"Login Result: {result}")
            
            # Get performance metrics
            metrics = login_page.get_performance_metrics()
            print(f"Performance Metrics: {metrics}")
            
            # Get accessibility information
            accessibility_info = await login_page.get_page_accessibility_info()
            print(f"Accessibility Info: {accessibility_info}")
            
            # Test logout if login was successful
            if result['success']:
                logout_result = await login_page.logout()
                print(f"Logout Result: {logout_result}")
            
        except Exception as e:
            print(f"Test execution error: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="login_test_error.png")
        
        finally:
            await page.close()
            await context.close()
            await browser.close()


@pytest.mark.smoke
@pytest.mark.critical
def test_basic_login_functionality():
    """
    Basic smoke test for login functionality
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            login_page = LoginPage(page)
            
            # Navigate to login page
            asyncio.run(login_page.navigate_to_login())
            
            # Test basic element finding
            username_element = asyncio.run(login_page._smart_find_element('username_field'))
            password_element = asyncio.run(login_page._smart_find_element('password_field'))
            login_button = asyncio.run(login_page._smart_find_element('login_button'))
            
            # Validate elements exist
            assert username_element is not None, "Username field not found"
            assert password_element is not None, "Password field not found"
            assert login_button is not None, "Login button not found"
            
            print("Basic login functionality test passed")
            
        except Exception as e:
            print(f"Basic login test failed: {e}")
            raise
        
        finally:
            browser.close()


@pytest.mark.ai_healing
def test_ai_healing_capabilities():
    """
    Test AI healing capabilities with broken selectors
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            login_page = LoginPage(page)
            
            # Navigate to login page
            asyncio.run(login_page.navigate_to_login())
            
            # Test AI healing with various element types
            healing_results = {}
            
            for element_type in ['username_field', 'password_field', 'login_button']:
                try:
                    # Use AI healing to find element
                    element = asyncio.run(login_page._ai_heal_element(element_type))
                    healing_results[element_type] = element is not None
                except Exception as e:
                    healing_results[element_type] = False
                    print(f"AI healing failed for {element_type}: {e}")
            
            print(f"AI Healing Results: {healing_results}")
            
            # At least one element should be found with AI healing
            assert any(healing_results.values()), "AI healing failed for all elements"
            
        except Exception as e:
            print(f"AI healing test error: {e}")
            raise
        
        finally:
            browser.close()


@pytest.mark.performance
def test_login_performance():
    """
    Test login page performance
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            login_page = LoginPage(page)
            
            # Measure page load performance
            start_time = asyncio.get_event_loop().time()
            asyncio.run(login_page.navigate_to_login())
            load_time = asyncio.get_event_loop().time() - start_time
            
            # Get performance metrics
            metrics = login_page.get_performance_metrics()
            
            # Performance assertions
            assert load_time < 10.0, f"Page load too slow: {load_time:.2f}s"
            assert 'page_load_time' in metrics, "Page load time not measured"
            
            print(f"Performance test passed - Load time: {load_time:.2f}s")
            print(f"Metrics: {metrics}")
            
        except Exception as e:
            print(f"Performance test error: {e}")
            raise
        
        finally:
            browser.close()


if __name__ == "__main__":
    # Run the main demo
    test_ai_recovery_demo()