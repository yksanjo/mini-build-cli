#!/usr/bin/env python3
"""
Simple Crunchbase scraper that just logs in and accesses discovery page
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

async def main():
    print("="*60)
    print("Simple Crunchbase Scraper")
    print("="*60)
    
    # Load credentials
    with open('.crunchbase_credentials.json', 'r') as f:
        credentials = json.load(f)
    
    email = credentials['email']
    password = credentials['password']
    
    print(f"\nUsing email: {email}")
    
    # Start Playwright
    playwright = await async_playwright().start()
    
    # Launch browser (visible)
    browser = await playwright.chromium.launch(
        headless=False,
        slow_mo=100,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--window-size=1920,1080',
        ]
    )
    
    # Create context
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    page = await context.new_page()
    
    try:
        print("\n1. Going to Crunchbase homepage...")
        await page.goto('https://www.crunchbase.com', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("2. Going to login page...")
        await page.goto('https://www.crunchbase.com/login', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("3. Looking for login form...")
        # Try different selectors
        selectors = [
            'input[name="email"]',
            'input[type="email"]',
            '#email',
            'input[data-testid="email"]'
        ]
        
        found = False
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"   Found selector: {selector}")
                found = True
                break
            except:
                continue
        
        if not found:
            print("   ❌ Could not find email field")
            # Take screenshot
            await page.screenshot(path='login_page_debug.png')
            print("   Screenshot saved: login_page_debug.png")
            return
        
        print("4. Filling credentials...")
        await page.fill('input[name="email"]', email)
        await page.wait_for_timeout(1000)
        await page.fill('input[name="password"]', password)
        await page.wait_for_timeout(1000)
        
        print("5. Clicking login...")
        await page.click('button[type="submit"]')
        
        print("6. Waiting for login...")
        await page.wait_for_timeout(5000)
        
        # Check URL
        current_url = page.url
        print(f"\nCurrent URL: {current_url}")
        
        if 'login' not in current_url:
            print("✅ Login successful!")
            
            # Go to discovery page
            print("\n7. Going to discovery page...")
            await page.goto('https://www.crunchbase.com/discover/organization.companies', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # Take screenshot
            await page.screenshot(path='discovery_page_simple.png')
            print("   Screenshot saved: discovery_page_simple.png")
            
            # Try to extract some data
            print("\n8. Trying to extract company names...")
            
            # Try different selectors for company cards
            company_selectors = [
                '.grid-card',
                '.search-result',
                '.company-card',
                '[class*="company"]',
                '[class*="card"]'
            ]
            
            for selector in company_selectors:
                count = await page.evaluate(f"""
                    () => {{
                        const elements = document.querySelectorAll('{selector}');
                        return elements.length;
                    }}
                """)
                if count > 0:
                    print(f"   Found {count} elements with selector: {selector}")
                    
                    # Try to get text from first few
                    companies = await page.evaluate(f"""
                        () => {{
                            const elements = document.querySelectorAll('{selector}');
                            const names = [];
                            for (let i = 0; i < Math.min(5, elements.length); i++) {{
                                const text = elements[i].textContent.trim().substring(0, 100);
                                names.push(text);
                            }}
                            return names;
                        }}
                    """)
                    
                    print("\n   Sample company data:")
                    for i, name in enumerate(companies, 1):
                        print(f"   {i}. {name}")
                    break
            
            print("\n✅ Scraping test completed!")
            
        else:
            print("❌ Still on login page")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\nCleaning up...")
        await browser.close()
        await playwright.stop()
        print("Done!")

if __name__ == '__main__':
    asyncio.run(main())