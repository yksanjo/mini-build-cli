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
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
            color_scheme='light',
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        self.page = await self.context.new_page()
        return self.playwright
    
    async def login(self, email: str, password: str) -> bool:
        """Login to Crunchbase"""
        try:
            logger.info("Navigating to login page...")
            await self.page.goto('https://www.crunchbase.com/login', wait_until='networkidle')
            
            # Wait for login form
            await self.page.wait_for_selector('input[name="email"]', timeout=10000)
            
            # Fill credentials
            await self.page.fill('input[name="email"]', email)
            await self.page.fill('input[name="password"]', password)
            
            # Click login button
            await self.page.click('button[type="submit"]')
            
            # Wait for login to complete
            await self.page.wait_for_timeout(3000)
            
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
        if not self.logged_in:
            logger.error("Not logged in. Please login first.")
            return []
        
        try:
            logger.info(f"Navigating to discovery page: {url}")
            await self.page.goto(url, wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            # Take screenshot for debugging
            await self.page.screenshot(path='discovery_page.png')
            logger.info("Screenshot saved: discovery_page.png")
            
            companies = []
            seen_slugs = set()
            
            # Scroll to load more content
            logger.info("Scrolling to load content...")
            for _ in range(5):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(1000)
            
            # Try different selectors for company cards
            selectors = [
                'a[href*="/organization/"]',
                '.card',
                '.search-result',
                '.grid-item',
                '[data-test="search-result"]',
                '.component--card'
            ]
            
            for selector in selectors:
                cards = await self.page.query_selector_all(selector)
                if cards and len(cards) > 0:
                    logger.info(f"Found {len(cards)} elements with selector: {selector}")
                    break
            
            if not cards or len(cards) == 0:
                logger.warning("No company cards found. Trying to extract from page content...")
                # Fallback: extract all organization links
                org_links = await self.page.query_selector_all('a[href*="/organization/"]')
                cards = org_links
            
            logger.info(f"Processing {len(cards)} potential company elements...")
            
            for i, card in enumerate(cards[:max_companies]):
                try:
                    # Extract company data
                    company_data = await self._extract_company_from_card(card)
                    
                    if company_data and company_data.get('slug'):
                        slug = company_data['slug']
                        if slug not in seen_slugs:
                            seen_slugs.add(slug)
                            companies.append(company_data)
                            logger.info(f"  [{len(companies)}] Found: {company_data.get('name', slug)}")
                    
                    # Be polite
                    if i % 10 == 0:
                        await self.page.wait_for_timeout(500)
                        
                except Exception as e:
                    logger.debug(f"Error processing card {i}: {e}")
                    continue
            
            logger.info(f"Total companies extracted: {len(companies)}")
            return companies
            
        except Exception as e:
            logger.error(f"Error scraping discovery page: {e}")
            return []
    
    async def _extract_company_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract company data from a card element"""
        try:
            # Get the link
            link_element = await card.query_selector('a[href*="/organization/"]')
            if not link_element:
                # Maybe the card itself is a link
                href = await card.get_attribute('href')
                if not href or '/organization/' not in href:
                    return None
                link_element = card
            else:
                href = await link_element.get_attribute('href')
            
            # Extract slug from URL
            slug = None
            if href:
                # Extract slug from /organization/{slug} pattern
                parts = href.split('/organization/')
                if len(parts) > 1:
                    slug = parts[1].split('/')[0].split('?')[0]
            
            if not slug:
                return None
            
            # Try to get company name
            name = None
            name_selectors = [
                'h3', 'h4', '.card-title', '.company-name', 
                '[data-test="entity-name"]', '.title'
            ]
            
            for selector in name_selectors:
                name_element = await card.query_selector(selector)
                if name_element:
                    name_text = await name_element.text_content()
                    if name_text and len(name_text.strip()) > 0:
                        name = name_text.strip()
                        break
            
            # Try to get description
            description = None
            desc_selectors = [
                'p', '.description', '.card-text', 
                '[data-test="entity-description"]', '.summary'
            ]
            
            for selector in desc_selectors:
                desc_element = await card.query_selector(selector)
                if desc_element:
                    desc_text = await desc_element.text_content()
                    if desc_text and len(desc_text.strip()) > 0:
                        description = desc_text.strip()
                        break
            
            # Try to get location
            location = None
            location_selectors = [
                '.location', '[data-test="location"]', 
                '.geo', '.address'
            ]
            
            for selector in location_selectors:
                loc_element = await card.query_selector(selector)
                if loc_element:
                    loc_text = await loc_element.text_content()
                    if loc_text and len(loc_text.strip()) > 0:
                        location = loc_text.strip()
                        break
            
            # Try to get funding/other info
            funding = None
            funding_selectors = [
                '.funding', '.money', '.currency',
                '[data-test="funding"]'
            ]
            
            for selector in funding_selectors:
                fund_element = await card.query_selector(selector)
                if fund_element:
                    fund_text = await fund_element.text_content()
                    if fund_text and len(fund_text.strip()) > 0:
                        funding = fund_text.strip()
                        break
            
            return {
                'slug': slug,
                'name': name,
                'description': description,
                'location': location,
                'funding': funding,
                'url': f"https://www.crunchbase.com/organization/{slug}",
                'discovery_url': href if href else None,
                'extracted_at': time.time()
            }
            
        except Exception as e:
            logger.debug(f"Error extracting company data: {e}")
            return None
    
    async def scrape_multiple_pages(self, base_url: str, pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape multiple pages of discovery results"""
        all_companies = []
        
        for page_num in range(1, pages + 1):
            logger.info(f"Scraping page {page_num}...")
            
            # Build URL with page parameter
            if '?' in base_url:
                page_url = f"{base_url}&page={page_num}"
            else:
                page_url = f"{base_url}?page={page_num}"
            
            companies = await self.scrape_discovery_page(page_url, max_companies=50)
            all_companies.extend(companies)
            
            logger.info(f"Page {page_num}: Found {len(companies)} companies (Total: {len(all_companies)})")
            
            # Be polite between pages
            if page_num < pages:
                delay = random.uniform(3, 7)
                logger.info(f"Waiting {delay:.1f} seconds before next page...")
                await asyncio.sleep(delay)
        
        # Remove duplicates
        unique_companies = []
        seen_slugs = set()
        
        for company in all_companies:
            slug = company.get('slug')
            if slug and slug not in seen_slugs:
                seen_slugs.add(slug)
                unique_companies.append(company)
        
        logger.info(f"Total unique companies: {len(unique_companies)}")
        return unique_companies
    
    async def close(self):
        """Close browser"""
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
        
        # Scrape multiple pages
        companies = await scraper.scrape_multiple_pages(discovery_url, pages=3)
        
        if companies:
            print(f"\n✓ Successfully scraped {len(companies)} companies!")
            
            # Save results
            output_file = 'crunchbase_discovery_companies.json'
            with open(output_file, 'w') as f:
                json.dump({
                    'scraped_at': time.time(),
                    'total_companies': len(companies),
                    'source_url': discovery_url,
                    'companies': companies
                }, f, indent=2)
            
            print(f"✓ Data saved to {output_file}")
            
            # Show sample
            print("\nSample companies:")
            print("-" * 50)
            for i, company in enumerate(companies[:5]):
                print(f"{i+1}. {company.get('name', 'Unknown')}")
                print(f"   Slug: {company.get('slug')}")
                if company.get('location'):
                    print(f"   Location: {company.get('location')}")
                if company.get('funding'):
                    print(f"   Funding: {company.get('funding')}")
                print()
            
            # Also save as CSV for easy viewing
            csv_file = 'crunchbase_discovery_companies.csv'
            with open(csv_file, 'w') as f:
                f.write("Name,Slug,Location,Funding,URL\n")
                for company in companies:
                    name = company.get('name', '').replace(',', ';')
                    slug = company.get('slug', '')
                    location = company.get('location', '').replace(',', ';')
                    funding = company.get('funding', '').replace(',', ';')
                    url = company.get('url', '')
                    f.write(f'"{name}","{slug}","{location}","{funding}","{url}"\n')
            
            print(f"✓ CSV saved to {csv_file}")
            
        else:
            print("\n❌ No companies found. Possible reasons:")
            print("  1. Page structure may have changed")
            print("  2. Account may not have access to discovery features")
            print("  3. Rate limiting or blocking")
            print("\nCheck discovery_page.png for what the scraper saw.")
        
        print("\n" + "="*60)
        print("Browser will stay open for 30 seconds...")
        print("Press Ctrl+C to close early.")
        
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await scraper.close()
        print("\nCleanup complete")

if __name__ == "__main__":
    asyncio.run(main())