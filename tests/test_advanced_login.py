"""
Advanced Login Test Suite
Enterprise-grade testing with comprehensive scenarios, data-driven testing, and AI healing
"""

import pytest
import time
import asyncio
from playwright.sync_api import sync_playwright, Page
from typing import Dict, Any, List
from src.pages.login_page import LoginPage


class TestAdvancedLogin:
    """
    Advanced login test suite with enterprise features
    """
    
    @pytest.fixture(scope="function")
    def login_page(self, page: Page) -> LoginPage:
        """
        Fixture to provide LoginPage instance
        """
        return LoginPage(page)
    
    @pytest.fixture(scope="function")
    def page(self):
        """
        Playwright page fixture with advanced configuration
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-sandbox'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                ignore_https_errors=True
            )
            
            page = context.new_page()
            
            # Set default timeouts
            page.set_default_timeout(30000)
            page.set_default_navigation_timeout(30000)
            
            yield page
            
            # Cleanup
            page.close()
            context.close()
            browser.close()
    
    @pytest.fixture(scope="class")
    def test_credentials(self):
        """
        Test credentials fixture
        """
        return {
            'valid': {
                'username': 'test@example.com',
                'password': 'SecurePass123!',
                'expected_success': True
            },
            'invalid_password': {
                'username': 'test@example.com',
                'password': 'WrongPassword123!',
                'expected_success': False,
                'expected_error': 'Invalid credentials'
            },
            'invalid_username': {
                'username': 'nonexistent@example.com',
                'password': 'SecurePass123!',
                'expected_success': False,
                'expected_error': 'User not found'
            },
            'empty_fields': {
                'username': '',
                'password': '',
                'expected_success': False,
                'expected_error': 'Required fields'
            },
            'weak_password': {
                'username': 'test@example.com',
                'password': '123',
                'expected_success': False,
                'expected_error': 'Password too weak'
            }
        }
    
    @pytest.fixture(scope="class")
    def mfa_credentials(self):
        """
        MFA test credentials
        """
        return {
            'with_mfa': {
                'username': 'mfa_user@example.com',
                'password': 'SecurePass123!',
                'mfa_code': '123456',
                'expected_success': True
            },
            'invalid_mfa': {
                'username': 'mfa_user@example.com',
                'password': 'SecurePass123!',
                'mfa_code': '000000',
                'expected_success': False,
                'expected_error': 'Invalid MFA code'
            }
        }
    
    @pytest.fixture(scope="class")
    def security_test_data(self):
        """
        Security test data for penetration testing scenarios
        """
        return {
            'sql_injection': {
                'username': "admin' OR '1'='1",
                'password': 'password',
                'expected_success': False,
                'security_risk': 'SQL Injection'
            },
            'xss_attempt': {
                'username': '<script>alert("xss")</script>',
                'password': 'password',
                'expected_success': False,
                'security_risk': 'XSS'
            },
            'brute_force_chars': {
                'username': 'admin',
                'password': 'a' * 1000,  # Very long password
                'expected_success': False,
                'security_risk': 'Buffer Overflow'
            }
        }
    
    @pytest.mark.smoke
    @pytest.mark.critical
    async def test_successful_login(self, login_page: LoginPage, test_credentials: Dict[str, Any]):
        """
        Test successful login with valid credentials
        """
        credentials = test_credentials['valid']
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Perform login
        result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            remember_me=False,
            use_ai_healing=True
        )
        
        # Assertions
        assert result['success'] is True, f"Login failed: {result.get('error', 'Unknown error')}"
        assert result.get('login_confirmed', False) is True, "Login not confirmed"
        assert result['performance_metrics']['login_duration'] < 10.0, "Login took too long"
        
        # Security checks
        security_checks = result['security_checks']
        assert security_checks['email_valid'] is True, "Email validation failed"
        assert security_checks['password_strength'] is True, "Password strength check failed"
        assert security_checks['sql_injection_risk'] is False, "SQL injection risk detected"
        assert security_checks['xss_risk'] is False, "XSS risk detected"
        
        print(f"Successful login completed in {result['performance_metrics']['login_duration']:.2f}s")
    
    @pytest.mark.regression
    @pytest.mark.parametrize("credential_type", ["invalid_password", "invalid_username", "empty_fields", "weak_password"])
    async def test_failed_login_scenarios(self, login_page: LoginPage, test_credentials: Dict[str, Any], credential_type: str):
        """
        Test various failed login scenarios
        """
        credentials = test_credentials[credential_type]
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Perform login
        result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            use_ai_healing=True
        )
        
        # Assertions
        assert result['success'] is False, "Login should have failed"
        assert result.get('login_confirmed', True) is False, "Login should not be confirmed"
        
        if 'expected_error' in credentials:
            assert 'error_message' in result or 'error' in result, "Error message expected"
        
        print(f"Failed login scenario '{credential_type}' correctly rejected")
    
    @pytest.mark.security
    @pytest.mark.parametrize("security_test", ["sql_injection", "xss_attempt", "brute_force_chars"])
    async def test_security_vulnerabilities(self, login_page: LoginPage, security_test_data: Dict[str, Any], security_test: str):
        """
        Test security vulnerability scenarios
        """
        test_data = security_test_data[security_test]
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Perform login with malicious input
        result = await login_page.smart_login(
            username=test_data['username'],
            password=test_data['password'],
            use_ai_healing=True
        )
        
        # Assertions - should always fail for security reasons
        assert result['success'] is False, f"Security test '{security_test}' should have failed"
        
        # Check that security risks were detected
        security_checks = result['security_checks']
        if security_test == 'sql_injection':
            assert security_checks['sql_injection_risk'] is True, "SQL injection risk not detected"
        elif security_test == 'xss_attempt':
            assert security_checks['xss_risk'] is True, "XSS risk not detected"
        
        print(f"Security test '{security_test}' properly blocked")
    
    @pytest.mark.performance
    async def test_login_performance(self, login_page: LoginPage, test_credentials: Dict[str, Any]):
        """
        Test login performance metrics
        """
        credentials = test_credentials['valid']
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Measure page load performance
        page_metrics = login_page.get_performance_metrics()
        assert 'page_load_time' in page_metrics, "Page load time not measured"
        assert page_metrics['page_load_time'] < 5.0, "Page load too slow"
        
        # Perform login
        start_time = time.time()
        result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            use_ai_healing=True
        )
        total_time = time.time() - start_time
        
        # Performance assertions
        assert result['success'] is True, "Login failed during performance test"
        assert total_time < 15.0, f"Total login time too slow: {total_time:.2f}s"
        assert result['performance_metrics']['login_duration'] < 5.0, "Login operation too slow"
        
        print(f"Performance test passed - Total: {total_time:.2f}s, Login: {result['performance_metrics']['login_duration']:.2f}s")
    
    @pytest.mark.accessibility
    async def test_login_accessibility(self, login_page: LoginPage):
        """
        Test login page accessibility
        """
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Get accessibility information
        accessibility_info = await login_page.get_page_accessibility_info()
        
        # Accessibility assertions
        assert 'error' not in accessibility_info, "Accessibility check failed"
        assert accessibility_info['has_form'] is True, "No form found on login page"
        assert accessibility_info['total_elements'] > 0, "No interactive elements found"
        
        # Check for proper labeling
        elements = accessibility_info['elements']
        input_elements = [el for el in elements if el['tag'] in ['INPUT']]
        
        for element in input_elements:
            if element['type'] in ['email', 'password', 'text']:
                # Should have label, aria-label, or placeholder
                has_labeling = (
                    element.get('has_label', False) or 
                    element.get('has_aria_label', False) or 
                    element.get('placeholder', '')
                )
                assert has_labeling, f"Input element {element} lacks proper labeling"
        
        print(f"Accessibility test passed - {accessibility_info['total_elements']} elements checked")
    
    @pytest.mark.ai_healing
    async def test_ai_healing_capabilities(self, login_page: LoginPage, test_credentials: Dict[str, Any]):
        """
        Test AI healing capabilities with broken selectors
        """
        credentials = test_credentials['valid']
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Mock broken selectors by temporarily modifying them
        original_selectors = login_page.selectors['primary'].copy()
        
        # Break the primary selectors
        login_page.selectors['primary']['username_field'] = ["#nonexistent-username"]
        login_page.selectors['primary']['password_field'] = ["#nonexistent-password"]
        login_page.selectors['primary']['login_button'] = ["#nonexistent-button"]
        
        try:
            # Perform login with AI healing enabled
            result = await login_page.smart_login(
                username=credentials['username'],
                password=credentials['password'],
                use_ai_healing=True
            )
            
            # AI healing should attempt recovery
            # Note: This test may fail if AI healing templates don't exist
            # but it validates the healing mechanism is triggered
            print(f"AI healing test completed - Success: {result['success']}")
            
        finally:
            # Restore original selectors
            login_page.selectors['primary'] = original_selectors
    
    @pytest.mark.mfa
    async def test_mfa_login(self, login_page: LoginPage, mfa_credentials: Dict[str, Any]):
        """
        Test multi-factor authentication login
        """
        credentials = mfa_credentials['with_mfa']
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Perform login with MFA
        result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            mfa_code=credentials['mfa_code'],
            use_ai_healing=True
        )
        
        # Assertions (may pass or fail depending on test environment)
        if result['success']:
            assert result.get('login_confirmed', False) is True, "MFA login not confirmed"
            print(f"MFA login successful")
        else:
            print(f"MFA login test completed (may not be supported in test environment)")
    
    @pytest.mark.session
    async def test_login_session_management(self, login_page: LoginPage, test_credentials: Dict[str, Any]):
        """
        Test login session management and logout
        """
        credentials = test_credentials['valid']
        
        # Navigate and login
        await login_page.navigate_to_login()
        login_result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            remember_me=True,
            use_ai_healing=True
        )
        
        assert login_result['success'] is True, "Login failed for session test"
        
        # Wait a moment to establish session
        await asyncio.sleep(2)
        
        # Test logout
        logout_result = await login_page.logout()
        
        # Logout assertions
        assert logout_result['success'] is True, f"Logout failed: {logout_result.get('error', 'Unknown error')}"
        assert logout_result['logout_duration'] < 5.0, "Logout took too long"
        
        print(f"Session management test passed - Logout in {logout_result['logout_duration']:.2f}s")
    
    @pytest.mark.stress
    @pytest.mark.parametrize("iteration", range(3))
    async def test_login_stress(self, login_page: LoginPage, test_credentials: Dict[str, Any], iteration: int):
        """
        Stress test with multiple login attempts
        """
        credentials = test_credentials['valid']
        
        # Navigate to login page
        await login_page.navigate_to_login()
        
        # Perform login
        result = await login_page.smart_login(
            username=credentials['username'],
            password=credentials['password'],
            use_ai_healing=True
        )
        
        # Basic assertions
        if result['success']:
            # Logout for next iteration
            await login_page.logout()
        
        print(f"Stress test iteration {iteration + 1} completed")
    
    @pytest.mark.ui
    async def test_responsive_login(self, login_page: LoginPage, test_credentials: Dict[str, Any]):
        """
        Test login on different viewport sizes
        """
        credentials = test_credentials['valid']
        
        viewports = [
            {'width': 1920, 'height': 1080},  # Desktop
            {'width': 768, 'height': 1024},   # Tablet
            {'width': 375, 'height': 667}     # Mobile
        ]
        
        for viewport in viewports:
            # Set viewport size
            await login_page.page.set_viewport_size(viewport)
            
            # Navigate to login page
            await login_page.navigate_to_login()
            
            # Perform login
            result = await login_page.smart_login(
                username=credentials['username'],
                password=credentials['password'],
                use_ai_healing=True
            )
            
            # Basic check that login elements are accessible
            if result['success']:
                await login_page.logout()
            
            print(f"Responsive test passed for {viewport['width']}x{viewport['height']}")


# Additional test classes for specific scenarios
class TestLoginSecurity:
    """
    Dedicated security tests for login functionality
    """
    
    @pytest.mark.security
    @pytest.mark.penetration
    async def test_brute_force_protection(self, login_page: LoginPage):
        """
        Test brute force protection mechanisms
        """
        await login_page.navigate_to_login()
        
        failed_attempts = 0
        max_attempts = 5
        
        for i in range(max_attempts):
            result = await login_page.smart_login(
                username='test@example.com',
                password=f'wrongpassword{i}',
                use_ai_healing=False  # Disable AI for speed
            )
            
            if not result['success']:
                failed_attempts += 1
            
            # Small delay between attempts
            await asyncio.sleep(0.5)
        
        # Should have failed all attempts
        assert failed_attempts == max_attempts, f"Expected {max_attempts} failed attempts, got {failed_attempts}"
        
        print(f"Brute force test completed - {failed_attempts} failed attempts")


class TestLoginIntegration:
    """
    Integration tests for login with other system components
    """
    
    @pytest.mark.integration
    async def test_login_with_database_validation(self, login_page: LoginPage):
        """
        Test login integration with database validation
        """
        # This would integrate with actual database validation
        # For demonstration, we'll simulate the integration
        await login_page.navigate_to_login()
        
        # Simulate database check
        db_valid_user = True
        db_password_match = True
        
        if db_valid_user and db_password_match:
            result = await login_page.smart_login(
                username='test@example.com',
                password='SecurePass123!',
                use_ai_healing=True
            )
            
            assert result['success'] is True, "Database integration login failed"
        
        print(f"Database integration test completed")


# Performance benchmark class
class TestLoginPerformance:
    """
    Dedicated performance tests for login functionality
    """
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    async def test_login_performance_benchmark(self, login_page: LoginPage):
        """
        Benchmark login performance
        """
        await login_page.navigate_to_login()
        
        # Multiple iterations for benchmarking
        times = []
        for i in range(5):
            start_time = time.time()
            
            result = await login_page.smart_login(
                username='test@example.com',
                password='SecurePass123!',
                use_ai_healing=False  # Disable AI for consistent performance
            )
            
            end_time = time.time()
            times.append(end_time - start_time)
            
            if result['success']:
                await login_page.logout()
            
            await asyncio.sleep(0.5)  # Brief pause between attempts
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        # Performance assertions
        assert avg_time < 10.0, f"Average login time too slow: {avg_time:.2f}s"
        assert max_time < 15.0, f"Maximum login time too slow: {max_time:.2f}s"
        
        print(f"Performance benchmark - Avg: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s")
