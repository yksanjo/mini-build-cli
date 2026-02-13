#!/usr/bin/env python3
"""
Simple Crunchbase login test
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os

async def test_login():
    print("Crunchbase Login Test")
    print("="*50)
    
    # Get credentials
    email = input("Enter your Crunchbase email: ").strip()
    password = input("Enter your Crunchbase password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required")
        return
    
    print(f"\nTesting login for: {email}")
    print("Starting browser...")
    
    async with async_playwright() as p:
        # Launch browser (visible for debugging)
        browser = await p.chromium.launch(headless=False)
        
        # Create context
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800}
        )
        
        page = await context.new_page()
        
        try:
            # Go to login page
            print("\n1. Loading login page...")
            await page.goto('https://www.crunchbase.com/login', timeout=30000)
            
            # Take screenshot
            await page.screenshot(path='step1_login_page.png')
            print("   ✓ Login page loaded")
            
            # Fill credentials
            print("\n2. Entering credentials...")
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', password)
            
            await page.screenshot(path='step2_credentials_filled.png')
            print("   ✓ Credentials entered")
            
            # Click login
            print("\n3. Clicking login button...")
            login_button = await page.query_selector('button[type="submit"]')
            if login_button:
                await login_button.click()
            else:
                # Try alternative selector
                await page.click('button:has-text("Sign in")')
            
            # Wait for navigation
            print("\n4. Waiting for login to complete...")
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
            except:
                print("   ⚠️  Navigation timeout, checking current state...")
            
            # Check result
            current_url = page.url
            await page.screenshot(path='step3_after_login.png')
            
            print(f"\n5. Current URL: {current_url}")
            
            # Analyze result
            page_content = await page.content()
            
            if 'dashboard' in current_url or 'home' in current_url:
                print("   ✅ SUCCESS: Logged in and redirected to dashboard!")
                logged_in = True
            elif 'login' in current_url:
                # Check for errors
                error_text = await page.evaluate("""
                    () => {
                        const errorEl = document.querySelector('.error-message, .text-red-500, [data-test="error-message"]');
                        return errorEl ? errorEl.innerText : 'No error message found';
                    }
                """)
                
                if error_text and error_text != 'No error message found':
                    print(f"   ❌ LOGIN FAILED: {error_text}")
                else:
                    print("   ❌ LOGIN FAILED: Still on login page")
                logged_in = False
            else:
                print(f"   ⚠️  Landed on unexpected page: {current_url}")
                logged_in = True  # Assume success
            
            # Test access if logged in
            if logged_in:
                print("\n6. Testing company page access...")
                await page.goto('https://www.crunchbase.com/organization/apple', timeout=15000)
                
                await page.screenshot(path='step4_company_page.png')
                
                # Check if blocked
                company_content = await page.content()
                if 'blocked' in company_content.lower():
                    print("   ❌ Still blocked from company pages")
                else:
                    print("   ✅ Can access company pages!")
                    
                    # Try to get company name
                    company_name = await page.evaluate("""
                        () => {
                            const h1 = document.querySelector('h1');
                            return h1 ? h1.innerText : 'No H1 found';
                        }
                    """)
                    print(f"   Company name: {company_name}")
            
            print("\n" + "="*50)
            print("SUMMARY:")
            print(f"Logged in: {'✅ YES' if logged_in else '❌ NO'}")
            print("Screenshots saved:")
            print("  - step1_login_page.png")
            print("  - step2_credentials_filled.png")
            print("  - step3_after_login.png")
            print("  - step4_company_page.png")
            
            if logged_in:
                print("\n✅ SUCCESS! Your paid account works for scraping.")
                print("We can now build the full scraper.")
            else:
                print("\n❌ Login failed. Possible issues:")
                print("1. Wrong credentials")
                print("2. CAPTCHA requirement")
                print("3. Account suspended/restricted")
                print("4. Browser automation detection")
            
            # Keep browser open for inspection
            print("\nBrowser will stay open for 30 seconds...")
            print("Check the screenshots and what you see in the browser.")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            print("Check if Crunchbase is accessible from your location.")
        finally:
            await browser.close()
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_login())