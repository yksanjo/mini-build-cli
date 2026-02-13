#!/usr/bin/env python3
"""
Simple test to check if we can login to Crunchbase
"""

import asyncio
import json
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_login():
    """Test login with actual credentials"""
    print("Testing Crunchbase login...")
    
    # Load credentials
    with open('.crunchbase_credentials.json', 'r') as f:
        credentials = json.load(f)
    
    email = credentials['email']
    password = credentials['password']
    
    print(f"Using email: {email}")
    
    playwright = await async_playwright().start()
    
    # Launch browser with visible window
    browser = await playwright.chromium.launch(
        headless=False,
        slow_mo=100,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--window-size=1920,1080',
        ]
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    page = await context.new_page()
    
    try:
        print("Navigating to Crunchbase homepage...")
        await page.goto('https://www.crunchbase.com', timeout=60000)
        
        print("Checking if already logged in...")
        await page.wait_for_timeout(3000)
        
        # Try to go to login page
        print("Going to login page...")
        await page.goto('https://www.crunchbase.com/login', timeout=60000)
        
        # Wait for login form
        print("Waiting for login form...")
        await page.wait_for_selector('input[name="email"]', timeout=15000)
        
        print("Filling credentials...")
        await page.fill('input[name="email"]', email)
        await page.wait_for_timeout(1000)
        await page.fill('input[name="password"]', password)
        await page.wait_for_timeout(1000)
        
        print("Clicking login button...")
        await page.click('button[type="submit"]')
        
        print("Waiting for login to complete...")
        await page.wait_for_timeout(5000)
        
        # Check current URL
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if 'login' not in current_url:
            print("✅ Login appears successful!")
            
            # Take a screenshot
            await page.screenshot(path='login_success.png')
            print("Screenshot saved as login_success.png")
            
            # Try to access discovery page
            print("\nTrying to access discovery page...")
            await page.goto('https://www.crunchbase.com/discover/organization.companies', timeout=30000)
            
            await page.wait_for_timeout(3000)
            await page.screenshot(path='discovery_page.png')
            print("Discovery page screenshot saved as discovery_page.png")
            
            return True
        else:
            print("❌ Still on login page")
            
            # Check for error messages
            error_elements = await page.query_selector_all('.error-message, .alert-danger, [data-testid="error-message"]')
            if error_elements:
                for error in error_elements:
                    error_text = await error.text_content()
                    print(f"Error message: {error_text}")
            
            await page.screenshot(path='login_failed.png')
            print("Screenshot saved as login_failed.png")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == '__main__':
    result = asyncio.run(test_login())
    if result:
        print("\n✅ Login test passed!")
    else:
        print("\n❌ Login test failed!")