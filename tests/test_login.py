import pytest
from playwright.sync_api import sync_playwright
from src.pages.base_page import BasePage

def test_ai_recovery_demo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com") # Replace with your target app

        base = BasePage(page)
        # This will try to click a broken ID, then use the AI to find it visually
        base.smart_click("#broken-id-123", "login_button")

        browser.close()