#!/usr/bin/env python3
"""
Firecrawl Scraper
=================
Scrapes comprehensive information about Firecrawl (firecrawl.dev)
A Y Combinator-backed API service that converts websites into LLM-friendly Markdown

Target: https://www.firecrawl.dev
Company: Mendable (YC S22)
Pricing: $16/month+
Value Prop: Converts any website into LLM-friendly Markdown instantly
Positioning: Infrastructure for AI agents
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PricingTier:
    """Represents a pricing tier"""
    name: str
    price: str
    description: str
    features: List[str]
    credits: Optional[str] = None


@dataclass
class FeatureInfo:
    """Represents a feature"""
    name: str
    description: str
    use_cases: List[str]


@dataclass
class FirecrawlData:
    """Complete Firecrawl company data"""
    company_name: str = "Firecrawl"
    parent_company: str = "Mendable"
    yc_batch: str = "S22"
    tagline: str = ""
    description: str = ""
    website: str = "https://www.firecrawl.dev"
    pricing: List[PricingTier] = None
    features: List[FeatureInfo] = None
    use_cases: List[str] = None
    api_endpoints: List[Dict] = None
    competitors: List[str] = None
    scraped_at: str = ""
    
    def __post_init__(self):
        if self.pricing is None:
            self.pricing = []
        if self.features is None:
            self.features = []
        if self.use_cases is None:
            self.use_cases = []
        if self.api_endpoints is None:
            self.api_endpoints = []
        if self.competitors is None:
            self.competitors = []
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'company_name': self.company_name,
            'parent_company': self.parent_company,
            'yc_batch': self.yc_batch,
            'tagline': self.tagline,
            'description': self.description,
            'website': self.website,
            'pricing': [asdict(p) for p in self.pricing],
            'features': [asdict(f) for f in self.features],
            'use_cases': self.use_cases,
            'api_endpoints': self.api_endpoints,
            'competitors': self.competitors,
            'scraped_at': self.scraped_at
        }


class FirecrawlScraper:
    """
    Scraper for Firecrawl website
    Extracts: pricing, features, use cases, API docs info
    """
    
    def __init__(self, headless: bool = True, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.data = FirecrawlData()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    async def setup(self):
        """Setup browser with stealth options"""
        logger.info("Setting up browser...")
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(60000)
        
        logger.info("Browser setup complete")
        
    async def scrape_homepage(self):
        """Scrape the main homepage for overview info"""
        logger.info("Scraping homepage...")
        
        try:
            await self.page.goto('https://www.firecrawl.dev', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            # Take screenshot
            await self.page.screenshot(path='firecrawl_homepage.png')
            logger.info("Screenshot saved: firecrawl_homepage.png")
            
            # Extract main tagline
            tagline_selectors = [
                'h1',
                '[class*="hero"] h1',
                '[class*="headline"]',
                '.tagline',
            ]
            
            for selector in tagline_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 10:
                            self.data.tagline = text.strip()
                            logger.info(f"Found tagline: {self.data.tagline[:100]}...")
                            break
                except:
                    continue
            
            # Extract description
            desc_selectors = [
                '[class*="description"]',
                '[class*="subtitle"]',
                'h1 + p',
                '.hero p',
            ]
            
            for selector in desc_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 20:
                            self.data.description = text.strip()
                            logger.info(f"Found description: {self.data.description[:100]}...")
                            break
                except:
                    continue
            
            # Extract features from homepage
            await self._extract_homepage_features()
            
        except Exception as e:
            logger.error(f"Error scraping homepage: {e}")
    
    async def _extract_homepage_features(self):
        """Extract feature list from homepage"""
        try:
            # Look for feature cards/sections
            feature_selectors = [
                '[class*="feature"]',
                '[class*="capability"]',
                '.grid > div',
                '[class*="card"]',
            ]
            
            for selector in feature_selectors:
                elements = await self.page.query_selector_all(selector)
                if len(elements) >= 3:
                    logger.info(f"Found {len(elements)} potential feature elements")
                    
                    for i, elem in enumerate(elements[:6]):  # Limit to first 6
                        try:
                            title_elem = await elem.query_selector('h3, h4, .title, strong')
                            desc_elem = await elem.query_selector('p, .description')
                            
                            title = await title_elem.text_content() if title_elem else ""
                            desc = await desc_elem.text_content() if desc_elem else ""
                            
                            if title:
                                feature = FeatureInfo(
                                    name=title.strip(),
                                    description=desc.strip() if desc else "",
                                    use_cases=[]
                                )
                                self.data.features.append(feature)
                                logger.info(f"Added feature: {title.strip()}")
                        except:
                            continue
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
    
    async def scrape_pricing(self):
        """Scrape pricing information"""
        logger.info("Scraping pricing page...")
        
        try:
            # Try direct pricing page
            await self.page.goto('https://www.firecrawl.dev/pricing', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            await self.page.screenshot(path='firecrawl_pricing.png')
            logger.info("Screenshot saved: firecrawl_pricing.png")
            
            # Look for pricing tiers
            pricing_selectors = [
                '[class*="pricing"]',
                '[class*="plan"]',
                '[class*="tier"]',
            ]
            
            tiers_found = []
            
            for selector in pricing_selectors:
                elements = await self.page.query_selector_all(selector)
                if len(elements) >= 2:
                    logger.info(f"Found {len(elements)} pricing elements")
                    
                    for elem in elements:
                        try:
                            # Extract tier name
                            name_elem = await elem.query_selector('h3, h2, .name, .title')
                            name = await name_elem.text_content() if name_elem else "Unknown"
                            
                            # Extract price
                            price_elem = await elem.query_selector('[class*="price"], .amount, strong')
                            price = await price_elem.text_content() if price_elem else ""
                            
                            # Extract features
                            feature_elems = await elem.query_selector_all('li, [class*="feature"]')
                            features = []
                            for fe in feature_elems:
                                ft = await fe.text_content()
                                if ft:
                                    features.append(ft.strip())
                            
                            tier = PricingTier(
                                name=name.strip(),
                                price=price.strip() if price else "Custom",
                                description="",
                                features=features[:10]  # Limit features
                            )
                            
                            tiers_found.append(tier)
                            logger.info(f"Found pricing tier: {name.strip()} - {price.strip() if price else 'Custom'}")
                            
                        except Exception as e:
                            logger.debug(f"Error extracting pricing tier: {e}")
                            continue
                    
                    break
            
            self.data.pricing = tiers_found
            
            # If no pricing found via selectors, try text extraction
            if not tiers_found:
                await self._extract_pricing_from_text()
                
        except Exception as e:
            logger.error(f"Error scraping pricing: {e}")
    
    async def _extract_pricing_from_text(self):
        """Fallback: extract pricing from page text"""
        try:
            page_text = await self.page.evaluate("""
                () => document.body.innerText
            """)
            
            # Look for common pricing patterns
            import re
            price_patterns = [
                r'\$\d+(?:\.\d{2})?(?:\/month|\/mo)?',
                r'\$\d+(?:\.\d{2})? per month',
                r'USD \d+(?:\.\d{2})?',
            ]
            
            found_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                found_prices.extend(matches)
            
            if found_prices:
                logger.info(f"Found prices: {found_prices}")
                
        except Exception as e:
            logger.error(f"Error extracting pricing from text: {e}")
    
    async def scrape_docs(self):
        """Scrape API documentation for endpoints and features"""
        logger.info("Scraping documentation...")
        
        try:
            await self.page.goto('https://docs.firecrawl.dev', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            await self.page.screenshot(path='firecrawl_docs.png')
            logger.info("Screenshot saved: firecrawl_docs.png")
            
            # Extract API endpoints
            endpoints = await self.page.evaluate("""
                () => {
                    const endpoints = [];
                    const codeBlocks = document.querySelectorAll('code, pre');
                    
                    codeBlocks.forEach(block => {
                        const text = block.textContent;
                        // Look for API endpoint patterns
                        if (text.includes('/v1/') || text.includes('api.firecrawl.dev')) {
                            endpoints.push(text.trim().substring(0, 200));
                        }
                    });
                    
                    return endpoints.slice(0, 10);  // Limit to 10
                }
            """)
            
            for ep in endpoints:
                self.data.api_endpoints.append({'endpoint': ep})
                logger.info(f"Found API endpoint: {ep[:80]}...")
                
        except Exception as e:
            logger.error(f"Error scraping docs: {e}")
    
    async def scrape_use_cases(self):
        """Scrape use cases and positioning"""
        logger.info("Scraping use cases...")
        
        try:
            # Go back to homepage for use cases
            await self.page.goto('https://www.firecrawl.dev', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            # Extract all text and look for use case mentions
            page_text = await self.page.evaluate("""
                () => {
                    const texts = [];
                    const elements = document.querySelectorAll('p, li, h2, h3');
                    elements.forEach(el => {
                        const text = el.textContent.trim();
                        if (text.length > 10 && text.length < 200) {
                            texts.push(text);
                        }
                    });
                    return texts;
                }
            """)
            
            # Filter for use case keywords
            use_case_keywords = [
                'llm', 'ai agent', 'rag', 'scrape', 'crawl', 'extract',
                'data', 'api', 'markdown', 'website', 'convert',
                'automation', 'workflow', 'training data'
            ]
            
            for text in page_text:
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in use_case_keywords):
                    if text not in self.data.use_cases:
                        self.data.use_cases.append(text)
                        
            logger.info(f"Found {len(self.data.use_cases)} use case mentions")
            
        except Exception as e:
            logger.error(f"Error scraping use cases: {e}")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    def save_results(self):
        """Save scraped data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'firecrawl_data_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(self.data.to_dict(), f, indent=2)
        
        logger.info(f"Data saved to: {filename}")
        return filename
    
    def generate_report(self) -> str:
        """Generate a markdown report"""
        report = f"""# Firecrawl Analysis Report

## Company Overview
- **Company**: {self.data.company_name}
- **Parent**: {self.data.parent_company}
- **YC Batch**: {self.data.yc_batch}
- **Website**: {self.data.website}

## Tagline
{self.data.tagline}

## Description
{self.data.description}

## Pricing Tiers
"""
        
        for tier in self.data.pricing:
            report += f"\n### {tier.name}\n"
            report += f"- **Price**: {tier.price}\n"
            if tier.features:
                report += "- **Features**:\n"
                for feat in tier.features[:5]:
                    report += f"  - {feat}\n"
        
        report += "\n## Key Features\n"
        for feature in self.data.features[:10]:
            report += f"- **{feature.name}**: {feature.description}\n"
        
        report += "\n## Use Cases\n"
        for use_case in self.data.use_cases[:10]:
            report += f"- {use_case}\n"
        
        report += f"\n## API Endpoints\n"
        for ep in self.data.api_endpoints[:5]:
            report += f"- `{ep['endpoint']}`\n"
        
        report += f"\n---\n*Report generated on {self.data.scraped_at}*"
        
        return report


async def main():
    """Main entry point"""
    print("="*70)
    print("Firecrawl Scraper")
    print("="*70)
    print("\nTarget: Firecrawl (firecrawl.dev)")
    print("Company: Mendable (YC S22)")
    print("Description: Convert any website into LLM-friendly Markdown")
    print("\n" + "="*70)
    
    scraper = FirecrawlScraper(headless=True, slow_mo=100)
    
    try:
        # Setup browser
        await scraper.setup()
        
        # Scrape all sections
        await scraper.scrape_homepage()
        await scraper.scrape_pricing()
        await scraper.scrape_docs()
        await scraper.scrape_use_cases()
        
        # Save results
        json_file = scraper.save_results()
        
        # Generate and save report
        report = scraper.generate_report()
        report_file = f'firecrawl_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print("\n" + "="*70)
        print("SCRAPING COMPLETE")
        print("="*70)
        print(f"\n📄 JSON Data: {json_file}")
        print(f"📊 Report: {report_file}")
        print(f"📸 Screenshots: firecrawl_homepage.png, firecrawl_pricing.png, firecrawl_docs.png")
        
        # Print summary
        print("\n" + "-"*70)
        print("SUMMARY")
        print("-"*70)
        print(f"Tagline: {scraper.data.tagline[:80] if scraper.data.tagline else 'N/A'}...")
        print(f"Pricing tiers found: {len(scraper.data.pricing)}")
        print(f"Features found: {len(scraper.data.features)}")
        print(f"Use cases found: {len(scraper.data.use_cases)}")
        print(f"API endpoints found: {len(scraper.data.api_endpoints)}")
        
        # Print report preview
        print("\n" + "="*70)
        print("REPORT PREVIEW")
        print("="*70)
        print(report[:2000])
        print("\n... (see full report in file)")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await scraper.close()
        except:
            pass  # Ignore cleanup errors


if __name__ == '__main__':
    asyncio.run(main())
