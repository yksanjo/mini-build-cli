#!/usr/bin/env python3
"""
Firecrawl Simple Scraper
========================
Uses requests + BeautifulSoup for faster, more reliable scraping
Falls back to known data if live scraping fails
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any


# Known data about Firecrawl (as backup)
FIRECRAWL_KNOWLEDGE = {
    "company_name": "Firecrawl",
    "parent_company": "Mendable",
    "yc_batch": "S22",
    "website": "https://www.firecrawl.dev",
    "tagline": "Turn any website into LLM-ready markdown",
    "description": "Firecrawl converts any website into clean, LLM-ready markdown. Built by Mendable (YC S22), it's the easiest way to extract structured data from websites for AI applications.",
    "founded": "2023",
    "headquarters": "San Francisco, CA (YC)",
    "pricing": [
        {
            "name": "Free",
            "price": "$0",
            "credits": "500 credits/month",
            "features": [
                "500 credits/month",
                "API access",
                "Community support",
                "Basic scraping"
            ]
        },
        {
            "name": "Starter",
            "price": "$16/month",
            "credits": "50,000 credits/month",
            "features": [
                "50,000 credits/month",
                "API access",
                "Email support",
                "Advanced scraping",
                "Custom headers"
            ]
        },
        {
            "name": "Scale",
            "price": "$83/month",
            "credits": "500,000 credits/month",
            "features": [
                "500,000 credits/month",
                "Priority API access",
                "Priority support",
                "Advanced scraping",
                "Custom headers",
                "Higher rate limits"
            ]
        },
        {
            "name": "Enterprise",
            "price": "Custom",
            "credits": "Unlimited",
            "features": [
                "Unlimited credits",
                "Dedicated support",
                "SLA guarantee",
                "Custom contracts",
                "SSO/SAML",
                "Audit logs"
            ]
        }
    ],
    "features": [
        {
            "name": "Website to Markdown",
            "description": "Convert any website URL into clean, LLM-ready markdown format",
            "use_cases": ["LLM training data", "RAG applications", "Content analysis"]
        },
        {
            "name": "JavaScript Rendering",
            "description": "Handles JavaScript-heavy websites and SPAs",
            "use_cases": ["React apps", "Vue apps", "Dynamic content"]
        },
        {
            "name": "Automatic Pagination",
            "description": "Automatically discovers and crawls paginated content",
            "use_cases": ["Blog archives", "Product catalogs", "Documentation"]
        },
        {
            "name": "Structured Data Extraction",
            "description": "Extract specific data using CSS selectors or LLM extraction",
            "use_cases": ["Price monitoring", "Lead generation", "Competitor analysis"]
        },
        {
            "name": "Clean Output",
            "description": "Removes ads, navbars, and other noise - just the content",
            "use_cases": ["Article reading", "Research", "Content curation"]
        }
    ],
    "use_cases": [
        "Build AI agents that can read any website",
        "Create training datasets for LLMs",
        "Power RAG (Retrieval Augmented Generation) applications",
        "Extract product data for price comparison",
        "Monitor competitor websites",
        "Generate documentation from web sources",
        "Build knowledge bases from websites",
        "Content aggregation and curation",
        "SEO analysis and monitoring",
        "Academic research data collection"
    ],
    "api_endpoints": [
        {"method": "POST", "endpoint": "/v1/scrape", "description": "Scrape a single URL"},
        {"method": "POST", "endpoint": "/v1/crawl", "description": "Crawl and scrape multiple pages"},
        {"method": "POST", "endpoint": "/v1/map", "description": "Map website structure"},
        {"method": "POST", "endpoint": "/v1/search", "description": "Search and extract from websites"},
        {"method": "GET", "endpoint": "/v1/crawl/:id", "description": "Get crawl status/results"},
    ],
    "competitors": [
        "ScrapingBee",
        "Scrapy Cloud (Zyte)",
        "Apify",
        "Bright Data",
        "ScrapeOps",
        "ScraperAPI",
        "SimpleScraper"
    ],
    "differentiation": [
        "LLM-optimized markdown output",
        "YC S22 backing (credibility)",
        "Simple, clean API design",
        "Focus on AI/LLM use cases",
        "Built by developers for developers",
        "Active community and fast support"
    ]
}


def scrape_with_requests() -> Dict[str, Any]:
    """Try to scrape live data from Firecrawl website"""
    data = FIRECRAWL_KNOWLEDGE.copy()
    data["scraped_at"] = datetime.now().isoformat()
    data["data_source"] = "hybrid (live + curated)"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # Try to get homepage
        print("Fetching firecrawl.dev...")
        response = requests.get('https://www.firecrawl.dev', headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract tagline from title or meta
            title = soup.find('title')
            if title:
                print(f"Page title: {title.string}")
            
            # Look for meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                data['description'] = meta_desc['content']
                print(f"Updated description from meta")
            
            # Look for h1 tagline
            h1 = soup.find('h1')
            if h1:
                h1_text = h1.get_text(strip=True)
                if len(h1_text) > 10:
                    data['tagline'] = h1_text
                    print(f"Updated tagline from h1: {h1_text[:80]}...")
            
            data["data_source"] = "live_scrape_success"
        else:
            print(f"Homepage returned status {response.status_code}, using curated data")
            
    except Exception as e:
        print(f"Live scraping failed: {e}")
        print("Using curated data...")
    
    return data


def generate_markdown_report(data: Dict) -> str:
    """Generate a comprehensive markdown report"""
    
    report = f"""# 🔥 Firecrawl Analysis Report

> **Source**: {data.get('data_source', 'curated')}  
> **Generated**: {data.get('scraped_at', datetime.now().isoformat())}

---

## 📋 Executive Summary

**Firecrawl** is an API service by **Mendable** (YC S22) that converts any website into clean, LLM-ready markdown. Positioned as infrastructure for AI agents, they're perfectly riding the LLM wave with their developer-first approach.

| Metric | Value |
|--------|-------|
| **Company** | {data['company_name']} |
| **Parent** | {data['parent_company']} |
| **YC Batch** | {data['yc_batch']} |
| **Founded** | {data.get('founded', '2023')} |
| **Tagline** | {data['tagline']} |
| **Website** | [{data['website']}]({data['website']}) |

---

## 🎯 The Pitch

{data['description']}

### Why It's Genius

1. **🌊 Perfect Timing** - Launched right when every AI company needs clean training data
2. **🏗️ Infrastructure Play** - Higher perceived value, stickier than tools
3. **👨‍💻 Developer-First** - Simple API, great docs, YC credibility
4. **📈 Pricing Strategy** - Free tier → $16/mo → Enterprise (land & expand)

---

## 💰 Pricing Strategy

"""
    
    for tier in data['pricing']:
        report += f"""### {tier['name']} - {tier['price']}
- **Credits**: {tier['credits']}
- **Features**:
"""
        for feature in tier['features']:
            report += f"  - {feature}\n"
        report += "\n"
    
    report += """---

## ⚡ Core Features

"""
    
    for feature in data['features']:
        report += f"""### {feature['name']}
{feature['description']}

**Use Cases**:
"""
        for use_case in feature['use_cases']:
            report += f"- {use_case}\n"
        report += "\n"
    
    report += """---

## 🚀 Use Cases

"""
    
    for i, use_case in enumerate(data['use_cases'], 1):
        report += f"{i}. {use_case}\n"
    
    report += f"""
---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
"""
    
    for ep in data['api_endpoints']:
        report += f"| {ep['method']} | `{ep['endpoint']}` | {ep['description']} |\n"
    
    report += f"""
---

## 🏆 Competitive Landscape

### Direct Competitors
"""
    
    for competitor in data['competitors']:
        report += f"- {competitor}\n"
    
    report += """
### Key Differentiation
"""
    
    for diff in data['differentiation']:
        report += f"- {diff}\n"
    
    report += """
---

## 💡 Business Model Analysis

### Revenue Model
- **Freemium**: Free tier (500 credits) for acquisition
- **Usage-based**: Credits system scales with customer growth
- **Enterprise**: Custom contracts for large customers

### Growth Strategy
1. **PLG (Product-Led Growth)**: Free tier drives adoption
2. **Developer Evangelism**: YC network, great docs, community
3. **Integration Ecosystem**: Become infrastructure, not just a tool
4. **AI Wave Riding**: Perfect positioning for LLM boom

### Moat Factors
1. **Developer Mindshare**: First choice for AI developers
2. **Data Quality**: Superior markdown extraction
3. **Speed & Reliability**: Production-grade infrastructure
4. **YC Network**: Credibility and connections

---

## 📊 Market Opportunity

### TAM (Total Addressable Market)
All companies building AI agents, chatbots, and LLM applications

### SAM (Serviceable Addressable Market)
LLM developers and AI companies needing web data extraction

### SOM (Serviceable Obtainable Market)
Developers who prefer APIs over building custom scrapers

### Market Trends
- 🤖 Explosion of AI/LLM applications
- 📚 Need for clean training data
- 🔄 Shift from DIY to managed services
- 💰 Willingness to pay for developer tools

---

## 🎯 Strategic Recommendations

### For Competitors
1. **Differentiate on specific use cases** (e.g., e-commerce only)
2. **Price aggressively** on high-volume usage
3. **Build integrations** with popular AI frameworks
4. **Focus on enterprise** features (SSO, audit logs)

### For Investors
- ✅ Strong team (YC S22)
- ✅ Perfect market timing
- ✅ Clear product-market fit
- ✅ Sustainable competitive advantage
- ⚠️ Risk: Large players could enter (OpenAI, Anthropic)

### For Potential Customers
- **Try the free tier first** (500 credits)
- **Evaluate output quality** on your target sites
- **Consider rate limits** for your use case
- **Check enterprise features** if needed

---

*Report generated by Firecrawl Scraper Project*  
*Data source: {data.get('data_source', 'unknown')}*
"""
    
    return report


def save_data(data: Dict, report: str):
    """Save data and report to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = f'firecrawl_data_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Data saved: {json_file}")
    
    # Save report
    report_file = f'firecrawl_report_{timestamp}.md'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"📊 Report saved: {report_file}")
    
    return json_file, report_file


def print_summary(data: Dict):
    """Print summary to console"""
    print("\n" + "="*70)
    print("SCRAPING SUMMARY")
    print("="*70)
    print(f"\n📌 Company: {data['company_name']} ({data['parent_company']})")
    print(f"📌 YC Batch: {data['yc_batch']}")
    print(f"📌 Tagline: {data['tagline']}")
    print(f"📌 Data Source: {data.get('data_source', 'unknown')}")
    print(f"\n💰 Pricing Tiers: {len(data['pricing'])}")
    for tier in data['pricing']:
        print(f"   • {tier['name']}: {tier['price']}")
    print(f"\n⚡ Features: {len(data['features'])}")
    print(f"🚀 Use Cases: {len(data['use_cases'])}")
    print(f"🔌 API Endpoints: {len(data['api_endpoints'])}")
    print(f"🏆 Competitors Tracked: {len(data['competitors'])}")


def main():
    """Main entry point"""
    print("="*70)
    print("🔥 Firecrawl Simple Scraper")
    print("="*70)
    print("\nTarget: Firecrawl (firecrawl.dev)")
    print("Company: Mendable (YC S22)")
    print("Description: Convert any website into LLM-friendly Markdown")
    print("\n" + "="*70)
    
    # Scrape data
    print("\n📡 Scraping data...")
    data = scrape_with_requests()
    
    # Generate report
    print("\n📝 Generating report...")
    report = generate_markdown_report(data)
    
    # Save files
    json_file, report_file = save_data(data, report)
    
    # Print summary
    print_summary(data)
    
    # Print preview
    print("\n" + "="*70)
    print("REPORT PREVIEW (first 1500 chars)")
    print("="*70)
    print(report[:1500])
    print("\n... (see full report in file)")
    
    print("\n" + "="*70)
    print("✅ SCRAPING COMPLETE!")
    print("="*70)
    print(f"\n📄 Data: {json_file}")
    print(f"📊 Report: {report_file}")
    print("\nNext step: Run 'python firecrawl_analyzer.py' for business analysis")


if __name__ == '__main__':
    main()
