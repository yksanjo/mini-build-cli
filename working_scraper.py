#!/usr/bin/env python3
"""
Working Crunchbase Discovery Scraper
"""

import asyncio
import json
import csv
import time
from playwright.async_api import async_playwright

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
    
    # Launch browser
    browser = await playwright.chromium.launch(
        headless=False,
        slow_mo=50,
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
    
    companies = []
    
    try:
        print("\n1. Logging in to Crunchbase...")
        await page.goto('https://www.crunchbase.com/login', timeout=60000)
        await page.wait_for_timeout(2000)
        
        # Fill login form
        await page.fill('input[name="email"]', email)
        await page.wait_for_timeout(1000)
        await page.fill('input[name="password"]', password)
        await page.wait_for_timeout(1000)
        await page.click('button[type="submit"]')
        
        # Wait for login
        await page.wait_for_timeout(5000)
        
        # Check if login successful
        if 'login' in page.url:
            print("❌ Login failed")
            return
        
        print("✅ Login successful!")
        
        print("\n2. Navigating to discovery page...")
        await page.goto('https://www.crunchbase.com/discover/organization.companies', timeout=30000)
        await page.wait_for_timeout(5000)
        
        print("3. Waiting for page to load...")
        # Wait a bit more for dynamic content
        await page.wait_for_timeout(3000)
        
        print("4. Scrolling to load more content...")
        # Scroll multiple times to load all content
        for i in range(10):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Check if we're at the bottom
            at_bottom = await page.evaluate("""
                () => {
                    return window.innerHeight + window.pageYOffset >= document.body.scrollHeight - 100;
                }
            """)
            
            if at_bottom:
                print(f"   Reached bottom after {i+1} scrolls")
                break
        
        await page.wait_for_timeout(3000)
        
        print("\n5. Extracting company data...")
        
        # Method 1: Try to find company cards by looking for links to organization pages
        companies_data = await page.evaluate("""
            () => {
                const companies = [];
                
                // Find all links that look like company/organization links
                const links = document.querySelectorAll('a[href*="/organization/"]');
                
                links.forEach(link => {
                    const href = link.getAttribute('href');
                    const text = link.textContent.trim();
                    
                    // Only include if it looks like a company name (not empty, not just a number)
                    if (text && text.length > 1 && !/^\\d+$/.test(text)) {
                        // Try to find the card container
                        let card = link.closest('div[class*="card"], div[class*="result"], div[class*="item"], section, article');
                        
                        const company = {
                            name: text,
                            url: 'https://www.crunchbase.com' + href,
                            source: 'link'
                        };
                        
                        // If we found a card, try to get more info
                        if (card) {
                            // Look for location
                            const locationElem = card.querySelector('[class*="location"], [class*="address"], [class*="geo"]');
                            if (locationElem) {
                                company.location = locationElem.textContent.trim();
                            }
                            
                            // Look for description
                            const descElem = card.querySelector('[class*="description"], [class*="summary"], [class*="about"]');
                            if (descElem) {
                                company.description = descElem.textContent.trim();
                            }
                            
                            // Look for funding
                            const fundingElems = card.querySelectorAll('span, div');
                            fundingElems.forEach(elem => {
                                const text = elem.textContent.trim();
                                if (text.includes('$') || text.includes('Funding') || text.includes('funding')) {
                                    company.funding_info = text;
                                }
                            });
                        }
                        
                        companies.push(company);
                    }
                });
                
                return companies;
            }
        """)
        
        # Filter out duplicates by URL
        unique_companies = {}
        for company in companies_data:
            if company['url'] not in unique_companies:
                unique_companies[company['url']] = company
        
        companies = list(unique_companies.values())
        
        print(f"✅ Found {len(companies)} unique companies")
        
        if companies:
            print("\n6. Saving results...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Save as JSON
            json_file = f'crunchbase_companies_{timestamp}.json'
            with open(json_file, 'w') as f:
                json.dump(companies, f, indent=2)
            print(f"   JSON saved: {json_file}")
            
            # Save as CSV
            csv_file = f'crunchbase_companies_{timestamp}.csv'
            if companies:
                fieldnames = set()
                for company in companies:
                    fieldnames.update(company.keys())
                fieldnames = sorted(fieldnames)
                
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(companies)
                print(f"   CSV saved: {csv_file}")
            
            # Show sample
            print("\n7. Sample companies:")
            for i, company in enumerate(companies[:10], 1):
                print(f"{i}. {company.get('name', 'N/A')}")
                if company.get('location'):
                    print(f"   Location: {company['location']}")
                if company.get('description'):
                    desc = company['description'][:100] + '...' if len(company['description']) > 100 else company['description']
                    print(f"   Description: {desc}")
                print()
        
        else:
            print("\n❌ No companies found. The page structure might have changed.")
            print("   Taking screenshot for debugging...")
            await page.screenshot(path='debug_no_companies.png')
            print("   Screenshot saved: debug_no_companies.png")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n8. Cleaning up...")
        await browser.close()
        await playwright.stop()
        print("✅ Done!")

if __name__ == '__main__':
    asyncio.run(scrape_crunchbase())