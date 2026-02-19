"""
Advanced Login Page Object Model
Enterprise-grade implementation with AI healing, security features, and comprehensive element handling
"""

import time
import re
from typing import Optional, Dict, Any, List
from playwright.sync_api import Page, Locator, expect
from src.pages.base_page import BasePage
from src.model.healing import VisualHealer
from src.model.predictor import DefectPredictor


class LoginPage(BasePage):
    """
    Advanced Login Page Object with enterprise features:
    - AI-powered visual healing
    - Security validation
    - Multi-factor authentication support
    - Performance monitoring
    - Error handling and recovery
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.visual_healer = VisualHealer(threshold=0.8)
        self.defect_predictor = DefectPredictor()
        
        # Advanced selector strategies
        self.selectors = {
            'primary': {
                'username_field': [
                    "#username",
                    "input[name='username']",
                    "input[type='email']",
                    "input[placeholder*='email']",
                    "input[placeholder*='username']",
                    "[data-testid='username']"
                ],
                'password_field': [
                    "#password",
                    "input[name='password']",
                    "input[type='password']",
                    "[data-testid='password']"
                ],
                'login_button': [
                    "#login-button",
                    "button[type='submit']",
                    "button:has-text('Login')",
                    "button:has-text('Sign In')",
                    "input[type='submit']",
                    "[data-testid='login-button']"
                ],
                'remember_me': [
                    "#remember-me",
                    "input[name='remember']",
                    "input[type='checkbox']",
                    "[data-testid='remember-me']"
                ],
                'forgot_password': [
                    "a:has-text('Forgot')",
                    "a[href*='forgot']",
                    "[data-testid='forgot-password']"
                ],
                'error_message': [
                    ".error-message",
                    ".alert-danger",
                    "[data-testid='error']",
                    ".notification.error"
                ],
                'success_message': [
                    ".success-message",
                    ".alert-success",
                    "[data-testid='success']",
                    ".notification.success"
                ],
                'mfa_field': [
                    "#mfa-code",
                    "input[name='mfa']",
                    "input[placeholder*='code']",
                    "[data-testid='mfa-code']"
                ],
                'mfa_submit': [
                    "#mfa-submit",
                    "button:has-text('Verify')",
                    "button:has-text('Submit')",
                    "[data-testid='mfa-submit']"
                ]
            }
        }
        
        # Performance tracking
        self.performance_metrics = {}
        
        # Security patterns
        self.security_patterns = {
            'password_strength': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            'email_format': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'sql_injection': r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            'xss_patterns': r'(<script|javascript:|onload=|onerror=)'
        }
    
    async def navigate_to_login(self, url: str = "https://example.com/login") -> None:
        """
        Navigate to login page with performance monitoring
        """
        start_time = time.time()
        
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_load_state("networkidle")
            
            # Performance metrics
            load_time = time.time() - start_time
            self.performance_metrics['page_load_time'] = load_time
            
            # Security headers check
            await self._check_security_headers()
            
            # Page validation
            await self._validate_login_page()
            
        except Exception as e:
            await self._handle_navigation_error(e, url)
    
    async def _validate_login_page(self) -> None:
        """
        Validate that we're on the correct login page
        """
        # Check for login form elements
        login_indicators = [
            "input[type='password']",
            "button[type='submit']",
            "form",
            ":has-text('Login')",
            ":has-text('Sign In')"
        ]
        
        for indicator in login_indicators:
            try:
                element = self.page.locator(indicator).first
                if await element.count() > 0:
                    return
            except:
                continue
        
        raise Exception("Login page validation failed - no login form detected")
    
    async def _check_security_headers(self) -> None:
        """
        Check for security headers on the login page
        """
        response = await self.page.evaluate("""
            () => {
                const headers = {};
                for (const [key, value] of performance.getEntriesByType('navigation')[0].serverTimingEntries) {
                    headers[key] = value;
                }
                return headers;
            }
        """)
        
        # Log security headers for monitoring
        if response:
            self.performance_metrics['security_headers'] = response
    
    async def smart_login(self, username: str, password: str, 
                         remember_me: bool = False, 
                         mfa_code: Optional[str] = None,
                         use_ai_healing: bool = True) -> Dict[str, Any]:
        """
        Advanced login with AI healing, security checks, and comprehensive error handling
        """
        login_start_time = time.time()
        result = {
            'success': False,
            'error': None,
            'healing_used': False,
            'performance_metrics': {},
            'security_checks': {}
        }
        
        try:
            # Security validation
            await self._perform_security_checks(username, password, result)
            
            # Username field with AI healing
            username_element = await self._smart_find_element('username_field', use_ai_healing)
            if not username_element:
                raise Exception("Username field not found")
            
            await username_element.fill(username)
            await self._mask_input(username_element)  # Security feature
            
            # Password field with AI healing
            password_element = await self._smart_find_element('password_field', use_ai_healing)
            if not password_element:
                raise Exception("Password field not found")
            
            await password_element.fill(password)
            await self._mask_input(password_element)  # Security feature
            
            # Remember me option
            if remember_me:
                await self._handle_remember_me()
            
            # Login button with AI healing
            login_button = await self._smart_find_element('login_button', use_ai_healing)
            if not login_button:
                raise Exception("Login button not found")
            
            # Pre-login checks
            await self._pre_login_checks()
            
            # Click login button
            await self._smart_click(login_button, "login_button")
            
            # Handle MFA if required
            if mfa_code:
                await self._handle_mfa(mfa_code, use_ai_healing)
            
            # Post-login validation
            await self._validate_login_success(result)
            
            # Performance metrics
            login_duration = time.time() - login_start_time
            result['performance_metrics']['login_duration'] = login_duration
            self.performance_metrics['login_duration'] = login_duration
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            await self._handle_login_error(e, result)
        
        return result
    
    async def _smart_find_element(self, element_type: str, use_ai_healing: bool = True) -> Optional[Locator]:
        """
        Smart element finding with multiple fallback strategies
        """
        selectors = self.selectors['primary'][element_type]
        
        # Try each selector strategy
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    return element
            except:
                continue
        
        # AI healing fallback
        if use_ai_healing:
            return await self._ai_heal_element(element_type)
        
        return None
    
    async def _ai_heal_element(self, element_type: str) -> Optional[Locator]:
        """
        AI-powered visual healing for element location
        """
        try:
            # Take screenshot for visual analysis
            screenshot_path = f"temp_healing_{element_type}_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path)
            
            # Use visual healer to find element
            template_map = {
                'username_field': 'assets/templates/username_field.png',
                'password_field': 'assets/templates/password_field.png',
                'login_button': 'assets/templates/login_button.png'
            }
            
            if element_type in template_map:
                coords = self.visual_healer.find_element_visually(
                    screenshot_path, 
                    template_map[element_type]
                )
                
                if coords:
                    # Convert coordinates to click action
                    await self.page.mouse.click(coords[0], coords[1])
                    return self.page.locator(":focus")  # Return focused element
            
        except Exception as e:
            print(f"AI healing failed for {element_type}: {e}")
        
        return None
    
    async def _perform_security_checks(self, username: str, password: str, result: Dict[str, Any]) -> None:
        """
        Perform security validation on inputs
        """
        security_checks = result['security_checks']
        
        # Email format validation
        security_checks['email_valid'] = bool(re.match(self.security_patterns['email_format'], username))
        
        # Password strength check
        security_checks['password_strength'] = bool(re.match(self.security_patterns['password_strength'], password))
        
        # SQL injection check
        security_checks['sql_injection_risk'] = bool(re.search(self.security_patterns['sql_injection'], username.lower()))
        
        # XSS check
        security_checks['xss_risk'] = bool(re.search(self.security_patterns['xss_patterns'], username.lower() + password.lower()))
        
        # Log security concerns
        if security_checks['sql_injection_risk'] or security_checks['xss_risk']:
            print(f"SECURITY WARNING: Potential attack detected - {security_checks}")
    
    async def _mask_input(self, element: Locator) -> None:
        """
        Mask input fields for security (visual protection)
        """
        await element.evaluate("""(element) => {
            element.style.setProperty('-webkit-text-security', 'disc');
            element.style.setProperty('text-security', 'disc');
        }""")
    
    async def _handle_remember_me(self) -> None:
        """
        Handle remember me checkbox
        """
        remember_element = await self._smart_find_element('remember_me')
        if remember_element:
            await remember_element.check()
    
    async def _pre_login_checks(self) -> None:
        """
        Perform pre-login validation checks
        """
        # Check for network activity
        await self.page.wait_for_load_state("networkidle", timeout=5000)
        
        # Check for any visible error messages
        error_elements = await self.page.locator(".error, .alert-danger, [data-testid='error']").count()
        if error_elements > 0:
            print("Warning: Pre-login error messages detected")
    
    async def _smart_click(self, element: Locator, fallback_name: str) -> None:
        """
        Smart click with fallback strategies
        """
        try:
            await element.click()
        except Exception as e:
            print(f"Standard click failed, trying fallback: {e}")
            # Try JavaScript click
            await element.evaluate("element => element.click()")
            # Try coordinate click if available
            if hasattr(element, 'bounding_box'):
                box = await element.bounding_box()
                if box:
                    await self.page.mouse.click(box['x'] + box['width']//2, box['y'] + box['height']//2)
    
    async def _handle_mfa(self, mfa_code: str, use_ai_healing: bool = True) -> None:
        """
        Handle multi-factor authentication
        """
        # Wait for MFA field
        try:
            await self.page.wait_for_selector("input[placeholder*='code'], #mfa-code", timeout=10000)
        except:
            print("MFA field not found, assuming MFA not required")
            return
        
        mfa_field = await self._smart_find_element('mfa_field', use_ai_healing)
        if mfa_field:
            await mfa_field.fill(mfa_code)
            
            mfa_submit = await self._smart_find_element('mfa_submit', use_ai_healing)
            if mfa_submit:
                await mfa_submit.click()
    
    async def _validate_login_success(self, result: Dict[str, Any]) -> None:
        """
        Validate successful login
        """
        # Wait for navigation or success indicators
        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check for success indicators
            success_indicators = [
                ":has-text('Welcome')",
                ":has-text('Dashboard')",
                ":has-text('Home')",
                ".dashboard",
                ".user-profile",
                "[data-testid='dashboard']"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.page.locator(indicator).first
                    if await element.count() > 0 and await element.is_visible():
                        result['login_confirmed'] = True
                        return
                except:
                    continue
            
            # Check for redirect away from login page
            current_url = self.page.url
            if 'login' not in current_url.lower():
                result['login_confirmed'] = True
                return
            
            # If no success indicators found, check for errors
            await self._check_for_errors(result)
            
        except Exception as e:
            result['error'] = f"Login validation failed: {e}"
    
    async def _check_for_errors(self, result: Dict[str, Any]) -> None:
        """
        Check for error messages after login attempt
        """
        error_selectors = [
            ".error-message",
            ".alert-danger", 
            ".notification.error",
            "[data-testid='error']"
        ]
        
        for selector in error_selectors:
            try:
                error_element = self.page.locator(selector).first
                if await error_element.count() > 0 and await error_element.is_visible():
                    error_text = await error_element.text_content()
                    result['error_message'] = error_text
                    result['login_confirmed'] = False
                    return
            except:
                continue
        
        result['login_confirmed'] = False
        result['error'] = "Unable to confirm login success"
    
    async def _handle_navigation_error(self, error: Exception, url: str) -> None:
        """
        Handle navigation errors with recovery strategies
        """
        print(f"Navigation error for {url}: {error}")
        
        # Try alternative navigation
        try:
            await self.page.goto(url, wait_until="load")
            await self.page.wait_for_timeout(2000)
        except:
            # Final fallback - navigate without waiting
            await self.page.goto(url)
    
    async def _handle_login_error(self, error: Exception, result: Dict[str, Any]) -> None:
        """
        Handle login errors with detailed analysis
        """
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            result['error_type'] = 'timeout'
        elif 'not found' in error_str:
            result['error_type'] = 'element_not_found'
        elif 'network' in error_str:
            result['error_type'] = 'network_error'
        else:
            result['error_type'] = 'unknown'
        
        # Try to capture screenshot for debugging
        try:
            screenshot_path = f"login_error_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path)
            result['error_screenshot'] = screenshot_path
        except:
            pass
    
    async def logout(self) -> Dict[str, Any]:
        """
        Advanced logout with validation
        """
        logout_start_time = time.time()
        result = {'success': False, 'error': None}
        
        try:
            # Look for logout options
            logout_selectors = [
                "button:has-text('Logout')",
                "a:has-text('Logout')",
                "button:has-text('Sign Out')",
                "a:has-text('Sign Out')",
                "[data-testid='logout']",
                ".user-menu button",  # User menu dropdown
            ]
            
            logout_found = False
            for selector in logout_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0 and await element.is_visible():
                        await element.click()
                        logout_found = True
                        break
                except:
                    continue
            
            if not logout_found:
                # Try user menu approach
                user_menu = self.page.locator(".user-profile, .user-menu, [data-testid='user-menu']").first
                if await user_menu.count() > 0:
                    await user_menu.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Try logout again
                    for selector in logout_selectors[:3]:
                        try:
                            element = self.page.locator(selector).first
                            if await element.count() > 0:
                                await element.click()
                                logout_found = True
                                break
                        except:
                            continue
            
            if logout_found:
                await self.page.wait_for_load_state("networkidle")
                
                # Verify logout - check for login page or logout confirmation
                current_url = self.page.url
                if 'login' in current_url.lower() or 'logout' in current_url.lower():
                    result['success'] = True
                else:
                    result['error'] = "Logout confirmation failed"
            else:
                result['error'] = "Logout button not found"
            
            logout_duration = time.time() - logout_start_time
            result['logout_duration'] = logout_duration
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get all collected performance metrics
        """
        return self.performance_metrics
    
    async def get_page_accessibility_info(self) -> Dict[str, Any]:
        """
        Get accessibility information for the login page
        """
        try:
            accessibility_info = await self.page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input, button, a');
                    const accessibleElements = [];
                    
                    inputs.forEach(element => {
                        accessibleElements.push({
                            tag: element.tagName,
                            type: element.type,
                            has_label: element.labels && element.labels.length > 0,
                            has_aria_label: element.hasAttribute('aria-label'),
                            placeholder: element.placeholder,
                            id: element.id,
                            name: element.name
                        });
                    });
                    
                    return {
                        total_elements: accessibleElements.length,
                        elements: accessibleElements,
                        has_form: document.querySelector('form') !== null
                    };
                }
            """)
            
            return accessibility_info
        except Exception as e:
            return {'error': str(e)}
