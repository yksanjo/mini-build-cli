#!/usr/bin/env python3
"""
Final Crunchbase Scraper with improved anti-detection
"""

import asyncio
import json
import csv
import time
import random
from playwright.async_api import async_playwright

async def human_delay(min_ms=500, max_ms=2000):
    """Add human-like delay"""
    await asyncio.sleep(random.randint(min_ms, max_ms) / 1000)

async def scrape_crunchbase():
    print("="*60)
    print("Crunchbase Discovery Scraper")
    print("="*60)
    
    # Load credentials
    with open('.crunchbase_credentials.json', 'r') as f:
        credentials = json.load(f)
    
    email = credentials['email']
    password = credentials['password']
    
    print(f"\nUsing email: {email}")
    
    # Start Playwright
    playwright = await async_playwright().start()
    
    # Launch browser with more stealth options
    browser = await playwright.chromium.launch(
        headless=False,  # Keep visible for debugging
        slow_mo=100,     # Slow down operations
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--window-size=1920,1080',
            '--start-maximized'
        ]
    )
    
    # Create context with more realistic settings
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/Los_Angeles',
        permissions=['geolocation'],
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    )
    
    # Add stealth scripts
    await context.add_init_script("""
        // Overwrite navigator properties
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Overwrite plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Overwrite languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)
    
    page = await context.new_page()
    
    companies = []
    
    try:
        print("\n1. Going to Crunchbase homepage first...")
        await page.goto('https://www.crunchbase.com', 
                       wait_until='domcontentloaded',
                       timeout=60000)
        await human_delay(2000, 4000)
        
        print("2. Navigating to login page...")
        await page.goto('https://www.crunchbase.com/login', 
                       wait_until='domcontentloaded',
                       timeout=60000)
        await human_delay(2000, 3000)
        
        print("3. Looking for login form...")
        # Take screenshot to see what's on the page
        await page.screenshot(path='login_page_view.png')
        print("   Screenshot saved: login_page_view.png")
        
        # Try to find email field with multiple selectors
        email_selectors = [
            'input[name="email"]',
            'input[type="email"]',
            '#email',
            'input[data-testid="email"]',
            'input[placeholder*="email" i]',
            'input[placeholder*="mail" i]'
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = await page.wait_for_selector(selector, timeout=5000)
                if email_field:
                    print(f"   Found email field with: {selector}")
                    break
            except:
                continue
        
        if not email_field:
            print("   ❌ Could not find email field")
            # Show page content for debugging
            content = await page.content()
            print(f"   Page title: {await page.title()}")
            print(f"   Page URL: {page.url}")
            return
        
        print("4. Filling credentials...")
        # Type slowly like a human
        await email_field.click()
        await human_delay(500, 1000)
        
        for char in email:
            await email_field.type(char, delay=random.randint(50, 150))
            await asyncio.sleep(random.randint(10, 50) / 1000)
        
        await human_delay(1000, 1500)
        
        # Find password field
        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            '#password',
            'input[data-testid="password"]',
            'input[placeholder*="password" i]',
            'input[placeholder*="pass" i]'
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = await page.query_selector(selector)
                if password_field:
                    print(f"   Found password field with: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("   ❌ Could not find password field")
            return
        
        await password_field.click()
        await human_delay(500, 1000)
        
        for char in password:
            await password_field.type(char, delay=random.randint(50, 150))
            await asyncio.sleep(random.randint(10, 50) / 1000)
        
        await human_delay(1000, 1500)
        
        print("5. Clicking login button...")
        # Find and click submit button
        submit_selectors = [
            'button[type="submit"]',
            'button:has-text("Log In")',
            'button:has-text("Login")',
            'button:has-text("Sign In")',
            'input[type="submit"]',
            '[data-testid="login-button"]'
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = await page.query_selector(selector)
                if submit_button:
                    print(f"   Found submit button with: {selector}")
                    break
            except:
                continue
        
        if not submit_button:
            print("   ❌ Could not find submit button")
            return
        
        await submit_button.click()
        await human_delay(3000, 5000)
        
        # Check if login was successful
        current_url = page.url
        print(f"\n6. Current URL after login: {current_url}")
        
        if 'login' in current_url:
            print("❌ Login failed - still on login page")
            
            # Check for error messages
            error_text = await page.evaluate("""
                () => {
                    const errors = document.querySelectorAll('.error-message, .alert-danger, .text-red-500, [class*="error"]');
                    return errors.length > 0 ? errors[0].textContent.trim() : 'No error message found';
                }
            """)
            print(f"   Error: {error_text}")
            
            await page.screenshot(path='login_error.png')
            print("   Screenshot saved: login_error.png")
            return
        
        print("✅ Login successful!")
        await page.screenshot(path='login_success.png')
        print("   Screenshot saved: login_success.png")
        
        print("\n7. Navigating to discovery page...")
        await page.goto('https://www.crunchbase.com/discover/organization.companies', 
                       wait_until='domcontentloaded',
                       timeout=30000)
        await human_delay(3000, 5000)
        
        print("8. Scrolling to load content...")
        # Scroll multiple times
        for i in range(15):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
            await human_delay(1000, 2000)
            
            # Random scroll back up sometimes
            if random.random() > 0.7:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                await human_delay(500, 1000)
        
        await human_delay(2000, 3000)
        
        print("9. Taking final screenshot...")
        await page.screenshot(path='final_page.png')
        print("   Screenshot saved: final_page.png")
        
        print("\n10. Attempting to extract data...")
        # Since we're having trouble with selectors, let's get all text and filter
        all_text = await page.evaluate("""
            () => {
                return document.body.innerText;
            }
        """)
        
        # Save raw text for analysis
        with open('page_text.txt', 'w') as f:
            f.write(all_text)
        print("   Raw page text saved: page_text.txt")
        
        # Try to find company-like patterns in text
        lines = all_text.split('\n')
        company_lines = []
        
        for line in lines:
            line = line.strip()
            if (len(line) > 2 and len(line) < 100 and 
                not line.startswith('http') and
                not 'cookie' in line.lower() and
                not 'privacy' in line.lower() and
                not 'terms' in line.lower() and
                not '©' in line and
                not line.isdigit() and
                not line in ['Home', 'Discover', 'Search', 'Login', 'Sign Up']):
                company_lines.append(line)
        
        print(f"\nFound {len(company_lines)} potential company names/text snippets")
        
        if company_lines:
            # Create simple output
            companies = [{'name': line, 'extracted_from': 'text_analysis'} for line in company_lines[:100]]
            
            print("\n11. Saving results...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Save as JSON
            json_file = f'crunchbase_companies_{timestamp}.json'
            with open(json_file, 'w') as f:
                json.dump(companies, f, indent=2)
            print(f"   JSON saved: {json_file}")
            
            # Save as CSV
            csv_file = f'crunchbase_companies_{timestamp}.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'extracted_from'])
                for company in companies:
                    writer.writerow([company['name'], company['extracted_from']])
            print(f"   CSV saved: {csv_file}")
            
            # Show sample
            print("\n12. Sample findings:")
            for i, company in enumerate(companies[:20], 1):
                print(f"{i}. {company['name']}")
        
        else:
            print("\n❌ No company data could be extracted")
            print("   The page structure may require different scraping approach")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n13. Cleaning up...")
        await browser.close()
        await playwright.stop()
        print("✅ Scraping completed!")

if __name__ == '__main__':
    asyncio.run(scrape_crunchbase())