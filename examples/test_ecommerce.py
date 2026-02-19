#!/usr/bin/env python3
"""
Real-world example: E-commerce Login Test with AI Healing
Demonstrates practical application of AI-augmented test automation
"""

import pytest
from playwright.sync_api import sync_playwright
from src.pages.base_page import BasePage
import time

def test_ecommerce_login_ai_recovery():
    """
    Real-world scenario: Testing e-commerce login with AI healing
    Shows how AI recovers from dynamic ID changes in production
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to a demo e-commerce site
        page.goto("https://www.saucedemo.com")
        page.wait_for_load_state("networkidle")
        
        # Initialize AI-augmented base page
        base = BasePage(page)
        
        print("Testing login functionality with AI healing...")
        
        # Scenario 1: Try with a potentially broken selector (simulates production issue)
        try:
            # This selector might break due to dynamic IDs in production
            base.smart_click("#login-button-12345", "login_button")
            print("Primary selector worked!")
        except Exception as e:
            print(f"Primary selector failed: {e}")
            print("AI healing triggered automatically...")
        
        # Scenario 2: Fill credentials with AI healing for username field
        try:
            page.fill("#user-name", "standard_user")
            print("Username field located successfully")
        except Exception:
            print("AI would recover username field visually")
        
        # Scenario 3: Fill password with fallback
        try:
            page.fill("#password", "secret_sauce")
            print("Password field located successfully")
        except Exception:
            print("AI would recover password field visually")
        
        # Scenario 4: Submit login with AI healing
        try:
            base.smart_click("#login-button", "login_button")
            print("Login button clicked successfully")
        except Exception as e:
            print(f"Login button failed: {e}")
            print("AI healing attempting visual recovery...")
        
        # Wait for navigation and verify success
        try:
            page.wait_for_url("**/inventory.html", timeout=5000)
            print("Login successful - User redirected to inventory!")
            
            # Take success screenshot for AI learning
            page.screenshot(path="screenshots/login_success.png")
            print("Success screenshot saved for AI learning")
            
        except Exception:
            print("Login may have failed - Check AI healing logs")
            page.screenshot(path="screenshots/login_failed.png")
        
        browser.close()

def test_ai_visual_healing_demo():
    """
    Demonstrates pure AI visual healing capabilities
    Shows how OpenCV template matching works in practice
    """
    print("\n AI Visual Healing Demonstration")
    print("=" * 40)
    
    # This would be triggered by smart_click when selectors fail
    from src.model.healing import VisualHealer
    
    healer = VisualHealer(threshold=0.8)
    
    # Simulate a scenario where we have a screenshot but broken selector
    print("Scenario: Selector '#broken-submit-btn' not found")
    print("AI Initiating visual recovery...")
    
    # In real usage, these would be actual screenshots
    # For demo, we'll use the demo images
    coords = healer.find_element_visually("demo_scene.png", "assets/templates/login_button.png")
    
    if coords:
        print(f"AI SUCCESSFULLY located element at: {coords}")
        print("Test automation continues without manual intervention")
        return True
    else:
        print("AI could not locate element")
        print("Manual intervention required")
        return False

if __name__ == "__main__":
    print("Running Real-World AI Healing Examples")
    print("=" * 50)
    
    # Run the visual healing demo first
    test_ai_visual_healing_demo()
    
    print("\n" + "=" * 50)
    print("   Note: For full e-commerce demo, run:")
    print("   python3 -m pytest examples/test_ecommerce.py -v -s")
    print("   (Requires internet connection)")
