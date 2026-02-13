#!/usr/bin/env python3
"""
Modern Crunchbase Scraper (2025)
Hybrid approach: Requests + Playwright fallback
"""

import requests
import time
import random
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CrunchbaseScraper2025:
    """Modern Crunchbase scraper with multiple fallback strategies"""
    
    def __init__(self, use_playwright: bool = True, cache_dir: str = "./cache"):
        self.session = requests.Session()
        self.setup_headers()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.use_playwright = use_playwright
        
        if use_playwright:
            try:
                from playwright.sync_api import sync_playwright
                self.playwright_available = True
            except ImportError:
                logger.warning("Playwright not installed. Install with: pip install playwright && playwright install chromium")
                self.playwright_available = False
    
    def setup_headers(self):
        """Setup realistic browser headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    def get_cached(self, company_slug: str) -> Optional[Dict]:
        """Check cache for company data"""
        cache_file = self.cache_dir / f"{company_slug}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                # Check if cache is fresh (less than 7 days old)
                cache_time = datetime.fromisoformat(data.get('_cached_at', '2000-01-01'))
                if (datetime.now() - cache_time).days < 7:
                    logger.info(f"Using cached data for {company_slug}")
                    return data
        return None
    
    def save_cache(self, company_slug: str, data: Dict):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{company_slug}.json"
        data['_cached_at'] = datetime.now().isoformat()
        data['_source'] = 'scraped'
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Cached data for {company_slug}")
    
    def scrape_with_requests(self, url: str) -> Optional[str]:
        """Attempt to scrape using requests"""
        try:
            logger.info(f"Attempting requests scrape: {url}")
            response = self.session.get(url, timeout=10)
            
            # Check for blocking
            if response.status_code == 403:
                logger.warning("Got 403 - likely blocked")
                return None
            if response.status_code == 429:
                logger.warning("Rate limited (429)")
                return None
            
            response.raise_for_status()
            
            # Check for Cloudflare challenge
            if 'cf-chl-bypass' in response.text.lower() or 'cloudflare' in response.text.lower():
                logger.warning("Cloudflare protection detected")
                return None
            
            return response.text
            
        except Exception as e:
            logger.error(f"Requests scrape failed: {e}")
            return None
    
    def scrape_with_playwright(self, url: str) -> Optional[str]:
        """Fallback to Playwright for JS-heavy pages"""
        if not self.playwright_available:
            return None
            
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info(f"Attempting Playwright scrape: {url}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = context.new_page()
                
                # Add stealth
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page.goto(url, wait_until='networkidle')
                
                # Wait for content
                try:
                    page.wait_for_selector('h1', timeout=10000)
                except:
                    logger.warning("Timeout waiting for content")
                
                # Get page content
                content = page.content()
                
                browser.close()
                return content
                
        except Exception as e:
            logger.error(f"Playwright scrape failed: {e}")
            return None
    
    def parse_company_page(self, html: str) -> Dict[str, Any]:
        """Parse company data from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Basic extraction patterns (will need refinement)
        data = {
            'name': self._extract_text(soup, 'h1'),
            'description': self._extract_text(soup, '[data-test="description"]'),
            'website': self._extract_attr(soup, 'a[data-test="website"]', 'href'),
            'founded': self._extract_text(soup, '[data-test="founded-on"]'),
            'employee_count': self._extract_text(soup, '[data-test="employee-count"]'),
            'total_funding': self._extract_text(soup, '[data-test="total-funding"]'),
            'last_funding': self._extract_text(soup, '[data-test="last-funding"]'),
            'investors': self._extract_list(soup, '[data-test="investor-name"]'),
            'categories': self._extract_list(soup, '[data-test="category"]'),
            'scraped_at': datetime.now().isoformat(),
        }
        
        # Clean up data
        data = {k: v for k, v in data.items() if v not in [None, '', []]}
        
        return data
    
    def _extract_text(self, soup, selector: str) -> Optional[str]:
        """Extract text from selector"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None
    
    def _extract_attr(self, soup, selector: str, attr: str) -> Optional[str]:
        """Extract attribute from selector"""
        element = soup.select_one(selector)
        return element.get(attr) if element else None
    
    def _extract_list(self, soup, selector: str) -> list:
        """Extract list of items"""
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
    
    def scrape_company(self, company_slug: str) -> Optional[Dict]:
        """Main scraping method with fallbacks"""
        
        # Check cache first
        cached = self.get_cached(company_slug)
        if cached:
            return cached
        
        url = f"https://www.crunchbase.com/organization/{company_slug}"
        
        # Add random delay to be polite
        time.sleep(random.uniform(2, 5))
        
        # Try requests first
        html = self.scrape_with_requests(url)
        
        # Fallback to Playwright if needed
        if not html and self.use_playwright and self.playwright_available:
            logger.info("Falling back to Playwright...")
            html = self.scrape_with_playwright(url)
        
        if not html:
            logger.error(f"Failed to scrape {company_slug}")
            return None
        
        # Parse the data
        data = self.parse_company_page(html)
        
        if data:
            data['company_slug'] = company_slug
            data['url'] = url
            self.save_cache(company_slug, data)
        
        return data
    
    def scrape_multiple(self, company_slugs: list, max_workers: int = 3) -> Dict[str, Dict]:
        """Scrape multiple companies with rate limiting"""
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_slug = {
                executor.submit(self.scrape_company, slug): slug 
                for slug in company_slugs
            }
            
            for future in concurrent.futures.as_completed(future_to_slug):
                slug = future_to_slug[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        results[slug] = result
                        logger.info(f"Successfully scraped {slug}")
                    else:
                        logger.warning(f"Failed to scrape {slug}")
                except Exception as e:
                    logger.error(f"Error scraping {slug}: {e}")
                
                # Rate limiting between requests
                time.sleep(random.uniform(3, 7))
        
        return results

def main():
    """Example usage"""
    scraper = CrunchbaseScraper2025(use_playwright=True)
    
    # Test with some known companies
    test_companies = [
        "apple",
        "google",
        "airbnb",
        "stripe",
        "openai"
    ]
    
    print("Testing Crunchbase scraper...")
    print("=" * 50)
    
    for company in test_companies:
        print(f"\nScraping {company}...")
        data = scraper.scrape_company(company)
        
        if data:
            print(f"✓ Success: {data.get('name', 'N/A')}")
            print(f"  Website: {data.get('website', 'N/A')}")
            print(f"  Founded: {data.get('founded', 'N/A')}")
            print(f"  Employees: {data.get('employee_count', 'N/A')}")
        else:
            print(f"✗ Failed to scrape {company}")
        
        print("-" * 30)
    
    # Save results
    output_file = "crunchbase_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'companies': test_companies,
            'results': {c: scraper.get_cached(c) for c in test_companies}
        }, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()