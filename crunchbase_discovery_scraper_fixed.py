#!/usr/bin/env python3
"""
Crunchbase Discovery Page Scraper
Scrapes company listings from: https://www.crunchbase.com/discover/organization.companies
"""

import asyncio
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CrunchbaseDiscoveryScraper:
    """Scraper for Crunchbase discovery/search pages"""

    def __init__(self, headless: bool = False, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.context = None
        self.page = None
        self.browser = None
        self.playwright = None
        self.logged_in = False

    async def setup_browser(self):
        """Setup browser with stealth options"""
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.page = await self.context.new_page()

    async def login(self, email: str, password: str) -> bool:
        """Login to Crunchbase"""
        try:
            logger.info("Navigating to login page...")
            # Use longer timeout and domcontentloaded
            await self.page.goto('https://www.crunchbase.com/login', 
                                wait_until='domcontentloaded',
                                timeout=60000)

            # Wait for login form
            await self.page.wait_for_selector('input[name="email"]', timeout=15000)
            
            # Add human-like delays
            await self.page.wait_for_timeout(random.randint(1000, 2000))

            # Fill credentials
            await self.page.fill('input[name="email"]', email)
            await self.page.wait_for_timeout(random.randint(500, 1000))
            await self.page.fill('input[name="password"]', password)
            await self.page.wait_for_timeout(random.randint(500, 1000))

            # Click login button
            await self.page.click('button[type="submit"]')

            # Wait for login to complete
            await self.page.wait_for_timeout(5000)
            
            # Wait for page to load
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check if login was successful
            current_url = self.page.url
            if 'login' not in current_url:
                self.logged_in = True
                logger.info("Login successful!")
                return True
            else:
                # Check for error messages
                error_elements = await self.page.query_selector_all('.error-message, .alert-danger')
                if error_elements:
                    for error in error_elements:
                        error_text = await error.text_content()
                        logger.error(f"Login error: {error_text}")
                logger.error("Login failed - still on login page")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def scrape_discovery_page(self, url: str, max_companies: int = 50) -> List[Dict[str, Any]]:
        """Scrape company listings from discovery page"""
        companies = []
        
        try:
            logger.info(f"Navigating to discovery page: {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for company listings to load
            await self.page.wait_for_selector('.grid-row', timeout=15000)
            
            # Scroll to load more companies
            logger.info("Scrolling to load more companies...")
            for i in range(5):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(2000)
                
                # Check if we have enough companies
                current_count = await self.page.evaluate("""
                    () => {
                        const cards = document.querySelectorAll('.grid-row .grid-card');
                        return cards.length;
                    }
                """)
                
                logger.info(f"Loaded {current_count} companies so far...")
                if current_count >= max_companies:
                    break
            
            # Extract company data
            logger.info("Extracting company data...")
            companies = await self.page.evaluate("""
                () => {
                    const companies = [];
                    const cards = document.querySelectorAll('.grid-row .grid-card');
                    
                    cards.forEach(card => {
                        const company = {};
                        
                        // Get company name
                        const nameElem = card.querySelector('.component--grid-field-display-name a');
                        if (nameElem) {
                            company.name = nameElem.textContent.trim();
                            company.url = nameElem.href;
                        }
                        
                        // Get description
                        const descElem = card.querySelector('.component--grid-field-description');
                        if (descElem) {
                            company.description = descElem.textContent.trim();
                        }
                        
                        // Get location
                        const locationElem = card.querySelector('.component--grid-field-location');
                        if (locationElem) {
                            company.location = locationElem.textContent.trim();
                        }
                        
                        // Get funding
                        const fundingElem = card.querySelector('.component--grid-field-funding');
                        if (fundingElem) {
                            company.funding = fundingElem.textContent.trim();
                        }
                        
                        // Get last funding type
                        const fundingTypeElem = card.querySelector('.component--grid-field-last-funding-type');
                        if (fundingTypeElem) {
                            company.last_funding_type = fundingTypeElem.textContent.trim();
                        }
                        
                        // Get founded date
                        const foundedElem = card.querySelector('.component--grid-field-founded');
                        if (foundedElem) {
                            company.founded = foundedElem.textContent.trim();
                        }
                        
                        // Get employee count
                        const employeesElem = card.querySelector('.component--grid-field-employee-count');
                        if (employeesElem) {
                            company.employees = employeesElem.textContent.trim();
                        }
                        
                        // Get industries
                        const industriesElem = card.querySelector('.component--grid-field-industries');
                        if (industriesElem) {
                            company.industries = industriesElem.textContent.trim();
                        }
                        
                        if (company.name) {
                            companies.push(company);
                        }
                    });
                    
                    return companies;
                }
            """)
            
            logger.info(f"Successfully extracted {len(companies)} companies")
            
        except Exception as e:
            logger.error(f"Error scraping discovery page: {e}")
        
        return companies

    async def save_results(self, companies: List[Dict[str, Any]], format: str = 'both'):
        """Save results to file(s)"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if format in ['json', 'both']:
            json_file = f'crunchbase_companies_{timestamp}.json'
            with open(json_file, 'w') as f:
                json.dump(companies, f, indent=2)
            logger.info(f"Results saved to {json_file}")
        
        if format in ['csv', 'both']:
            csv_file = f'crunchbase_companies_{timestamp}.csv'
            if companies:
                import csv
                # Get all unique keys from all companies
                fieldnames = set()
                for company in companies:
                    fieldnames.update(company.keys())
                fieldnames = sorted(fieldnames)
                
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(companies)
                logger.info(f"Results saved to {csv_file}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")

async def main():
    """Main function"""
    print("="*60)
    print("Crunchbase Discovery Page Scraper")
    print("="*60)

    # Get credentials
    credentials_file = Path('.crunchbase_credentials.json')
    if not credentials_file.exists():
        print("\n❌ Credentials file not found!")
        print("Please create .crunchbase_credentials.json with:")
        print(json.dumps({"email": "your_email@example.com", "password": "your_password"}, indent=2))
        print("\nOr run: python3 create_credentials.py")
        return

    try:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return

    email = credentials.get('email')
    password = credentials.get('password')

    if not email or not password:
        print("❌ Email and password are required in credentials file")
        return

    print(f"\nUsing email: {email}")

    # Create scraper
    scraper = CrunchbaseDiscoveryScraper(headless=False, slow_mo=100)
    await scraper.setup_browser()

    try:
        # Login
        print("\nLogging in to Crunchbase...")
        login_success = await scraper.login(email, password)

        if not login_success:
            print("❌ Login failed")
            return

        print("✓ Login successful!")

        # Scrape discovery page
        discovery_url = "https://www.crunchbase.com/discover/organization.companies"
        print(f"\nScraping discovery page: {discovery_url}")
        print("This may take a few minutes...")
        
        companies = await scraper.scrape_discovery_page(discovery_url, max_companies=100)
        
        if companies:
            print(f"\n✓ Successfully scraped {len(companies)} companies!")
            
            # Save results
            await scraper.save_results(companies, format='both')
            
            # Show sample
            print("\nSample companies:")
            for i, company in enumerate(companies[:5], 1):
                print(f"{i}. {company.get('name', 'N/A')}")
                if company.get('location'):
                    print(f"   Location: {company['location']}")
                if company.get('funding'):
                    print(f"   Funding: {company['funding']}")
                print()
        else:
            print("\n❌ No companies found. The page structure might have changed.")

    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
    finally:
        print("\nCleanup complete")
        await scraper.cleanup()

if __name__ == '__main__':
    asyncio.run(main())