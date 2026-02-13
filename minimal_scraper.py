#!/usr/bin/env python3
"""
Minimal Crunchbase scraper - waits and tries gently
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

print("="*60)
print("MINIMAL Crunchbase Scraper")
print("="*60)
print("\n⚠️  Waiting 5 minutes to avoid rate limiting...")
print("   (Crunchbase blocked us for too many login attempts)")
print("   Starting at:", time.strftime("%H:%M:%S"))

# Wait 5 minutes
time.sleep(300)

print("\n✅ Wait complete. Starting scraper at:", time.strftime("%H:%M:%S"))

async def main():
    # Load credentials
    with open('.crunchbase_credentials.json', 'r') as f:
        credentials = json.load(f)
    
    email = credentials['email']
    password = credentials['password']
    
    print(f"\nUsing email: {email}")
    
    playwright = await async_playwright().start()
    
    # Very simple browser launch
    browser = await playwright.chromium.launch(
        headless=False,
        slow_mo=200  # Even slower
    )
    
    page = await browser.new_page()
    
    try:
        print("\n1. Going directly to login page...")
        await page.goto('https://www.crunchbase.com/login', timeout=90000)
        await page.wait_for_timeout(5000)
        
        print("2. Checking if we can see the form...")
        # Take screenshot
        await page.screenshot(path='current_login_page.png')
        
        # Check page content
        page_html = await page.content()
        if "too many times" in page_html:
            print("❌ Still rate limited. Need to wait longer.")
            return
        
        print("3. Trying to login VERY slowly...")
        await page.fill('input[name="email"]', email)
        await page.wait_for_timeout(3000)
        await page.fill('input[name="password"]', password)
        await page.wait_for_timeout(3000)
        await page.click('button[type="submit"]')
        
        print("4. Waiting for response...")
        await page.wait_for_timeout(10000)
        
        current_url = page.url
        print(f"\nCurrent URL: {current_url}")
        
        if 'login' not in current_url:
            print("✅ Login successful!")
            
            # Go to discovery
            print("\n5. Going to discovery page...")
            await page.goto('https://www.crunchbase.com/discover/organization.companies', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # Get simple text
            all_text = await page.evaluate("""
                () => {
                    // Get all text content
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    
                    const texts = [];
                    let node;
                    while (node = walker.nextNode()) {
                        const text = node.textContent.trim();
                        if (text && text.length > 2 && text.length < 100) {
                            texts.push(text);
                        }
                    }
                    return texts;
                }
            """)
            
            # Filter and deduplicate
            unique_texts = list(set(all_text))
            unique_texts.sort()
            
            print(f"\nFound {len(unique_texts)} text snippets")
            
            # Save results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f'crunchbase_data_{timestamp}.txt'
            
            with open(output_file, 'w') as f:
                f.write(f"Crunchbase Data - {timestamp}\n")
                f.write("="*50 + "\n\n")
                for i, text in enumerate(unique_texts[:200], 1):  # First 200
                    f.write(f"{i}. {text}\n")
            
            print(f"\n✅ Data saved to: {output_file}")
            
            # Show sample
            print("\nSample data:")
            for i, text in enumerate(unique_texts[:20], 1):
                print(f"{i}. {text}")
                
        else:
            print("❌ Still on login page")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await browser.close()
        await playwright.stop()
        print("\n✅ Done!")

if __name__ == '__main__':
    asyncio.run(main())