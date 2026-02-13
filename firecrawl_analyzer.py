#!/usr/bin/env python3
"""
Firecrawl Data Analyzer
=======================
Analyzes scraped Firecrawl data and generates insights
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class FirecrawlAnalyzer:
    """Analyzes Firecrawl data for business insights"""
    
    def __init__(self, data_file: str = None):
        self.data = None
        self.data_file = data_file
        
        if data_file and os.path.exists(data_file):
            self.load_data(data_file)
    
    def load_data(self, filename: str):
        """Load data from JSON file"""
        with open(filename, 'r') as f:
            self.data = json.load(f)
        print(f"Loaded data from {filename}")
    
    def find_latest_data_file(self) -> str:
        """Find the most recent firecrawl data file"""
        files = list(Path('.').glob('firecrawl_data_*.json'))
        if not files:
            raise FileNotFoundError("No firecrawl data files found")
        
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    def analyze_pricing(self) -> Dict:
        """Analyze pricing strategy"""
        if not self.data or 'pricing' not in self.data:
            return {}
        
        pricing = self.data['pricing']
        analysis = {
            'total_tiers': len(pricing),
            'has_free_tier': any('free' in p.get('name', '').lower() for p in pricing),
            'has_enterprise': any('enterprise' in p.get('name', '').lower() for p in pricing),
            'price_range': [],
            'strategy': 'unknown'
        }
        
        # Extract prices
        import re
        prices = []
        for tier in pricing:
            price_str = tier.get('price', '')
            matches = re.findall(r'\$(\d+(?:\.\d{2})?)', price_str)
            prices.extend([float(p) for p in matches])
        
        if prices:
            analysis['price_range'] = [min(prices), max(prices)]
            
            # Determine pricing strategy
            if len(prices) >= 2:
                ratio = max(prices) / min(prices) if min(prices) > 0 else 0
                if ratio > 10:
                    analysis['strategy'] = 'land_and_expand'
                elif ratio > 3:
                    analysis['strategy'] = 'good_better_best'
                else:
                    analysis['strategy'] = 'tiered_usage'
        
        return analysis
    
    def analyze_positioning(self) -> Dict:
        """Analyze market positioning"""
        if not self.data:
            return {}
        
        text_to_analyze = ' '.join([
            self.data.get('tagline', ''),
            self.data.get('description', ''),
            ' '.join(self.data.get('use_cases', []))
        ]).lower()
        
        positioning = {
            'target_audience': [],
            'key_benefits': [],
            'positioning_type': 'productivity_tool',
            'market_category': 'data_extraction'
        }
        
        # Detect target audience
        audience_signals = {
            'developers': ['api', 'sdk', 'developer', 'llm', 'ai'],
            'enterprises': ['enterprise', 'scale', 'team', 'organization'],
            'startups': ['startup', 'founder', 'yc', 'rapid'],
            'agencies': ['agency', 'client', 'multiple sites']
        }
        
        for audience, signals in audience_signals.items():
            if any(signal in text_to_analyze for signal in signals):
                positioning['target_audience'].append(audience)
        
        # Detect key benefits
        benefit_signals = {
            'time_saving': ['instant', 'automatic', 'fast', 'quick'],
            'cost_saving': ['free', 'cheap', 'affordable', 'save'],
            'accuracy': ['accurate', 'clean', 'structured', 'perfect'],
            'scalability': ['scale', 'unlimited', 'bulk', 'batch']
        }
        
        for benefit, signals in benefit_signals.items():
            if any(signal in text_to_analyze for signal in signals):
                positioning['key_benefits'].append(benefit)
        
        # Check for infrastructure positioning
        if any(word in text_to_analyze for word in ['infrastructure', 'platform', 'backend', 'service']):
            positioning['positioning_type'] = 'infrastructure'
        
        return positioning
    
    def analyze_features(self) -> Dict:
        """Analyze feature set"""
        if not self.data or 'features' not in self.data:
            return {}
        
        features = self.data['features']
        
        analysis = {
            'total_features': len(features),
            'categories': {},
            'core_capabilities': []
        }
        
        # Categorize features
        categories = {
            'extraction': ['scrape', 'extract', 'crawl', 'fetch', 'parse'],
            'formatting': ['markdown', 'json', 'html', 'clean', 'format'],
            'integration': ['api', 'sdk', 'webhook', 'integration'],
            'ai_ml': ['llm', 'ai', 'ml', 'embedding', 'vector'],
            'automation': ['schedule', 'auto', 'batch', 'sync']
        }
        
        for feature in features:
            name = feature.get('name', '').lower()
            desc = feature.get('description', '').lower()
            combined = name + ' ' + desc
            
            for category, signals in categories.items():
                if any(signal in combined for signal in signals):
                    if category not in analysis['categories']:
                        analysis['categories'][category] = []
                    analysis['categories'][category].append(feature.get('name'))
        
        # Identify core capabilities
        if 'extraction' in analysis['categories']:
            analysis['core_capabilities'].append('data_extraction')
        if 'formatting' in analysis['categories']:
            analysis['core_capabilities'].append('content_transformation')
        if 'ai_ml' in analysis['categories']:
            analysis['core_capabilities'].append('ai_ready_output')
        
        return analysis
    
    def generate_insights(self) -> List[str]:
        """Generate business insights"""
        insights = []
        
        # Pricing insights
        pricing_analysis = self.analyze_pricing()
        if pricing_analysis.get('strategy') == 'land_and_expand':
            insights.append("📈 Uses 'Land and Expand' pricing - low entry point, high growth potential")
        if pricing_analysis.get('has_free_tier'):
            insights.append("🎁 Free tier available - good for user acquisition and product-led growth")
        
        # Positioning insights
        positioning = self.analyze_positioning()
        if 'developers' in positioning.get('target_audience', []):
            insights.append("👨‍💻 Developer-focused positioning - API-first approach")
        if positioning.get('positioning_type') == 'infrastructure':
            insights.append("🏗️ Positioned as infrastructure - higher perceived value, stickier product")
        if 'ai_ready_output' in positioning.get('key_benefits', []):
            insights.append("🤖 AI/LLM-ready output - riding the AI wave perfectly")
        
        # Feature insights
        features = self.analyze_features()
        if 'content_transformation' in features.get('core_capabilities', []):
            insights.append("🔄 Content transformation focus - not just scraping, but formatting")
        if features.get('total_features', 0) > 5:
            insights.append(f"✨ Rich feature set ({features['total_features']} features) - comprehensive solution")
        
        return insights
    
    def generate_competitive_analysis(self) -> Dict:
        """Generate competitive landscape analysis"""
        return {
            'direct_competitors': [
                'ScrapingBee',
                'Scrapy Cloud',
                'Apify',
                'Bright Data',
                'ScrapeOps'
            ],
            'indirect_competitors': [
                'BeautifulSoup (DIY)',
                'Puppeteer/Playwright (DIY)',
                'Readability.js',
                'Mercury Parser'
            ],
            'differentiation': [
                'LLM-optimized output (Markdown)',
                'YC backing (credibility)',
                'Simple API design',
                'Focus on AI use cases'
            ],
            'moat_factors': [
                'Developer mindshare in AI community',
                'Integration ecosystem',
                'Quality of extracted content',
                'Speed and reliability'
            ]
        }
    
    def print_analysis(self):
        """Print complete analysis"""
        print("\n" + "="*70)
        print("FIRECRAWL BUSINESS ANALYSIS")
        print("="*70)
        
        # Company basics
        print(f"\n📋 COMPANY OVERVIEW")
        print(f"   Name: {self.data.get('company_name', 'N/A')}")
        print(f"   Parent: {self.data.get('parent_company', 'N/A')}")
        print(f"   YC Batch: {self.data.get('yc_batch', 'N/A')}")
        print(f"   Tagline: {self.data.get('tagline', 'N/A')[:80]}...")
        
        # Pricing analysis
        print(f"\n💰 PRICING ANALYSIS")
        pricing = self.analyze_pricing()
        print(f"   Tiers: {pricing.get('total_tiers', 'N/A')}")
        print(f"   Strategy: {pricing.get('strategy', 'N/A')}")
        print(f"   Has Free Tier: {pricing.get('has_free_tier', False)}")
        print(f"   Has Enterprise: {pricing.get('has_enterprise', False)}")
        if pricing.get('price_range'):
            print(f"   Price Range: ${pricing['price_range'][0]} - ${pricing['price_range'][1]}")
        
        # Positioning analysis
        print(f"\n🎯 POSITIONING ANALYSIS")
        positioning = self.analyze_positioning()
        print(f"   Type: {positioning.get('positioning_type', 'N/A')}")
        print(f"   Target Audience: {', '.join(positioning.get('target_audience', []))}")
        print(f"   Key Benefits: {', '.join(positioning.get('key_benefits', []))}")
        
        # Feature analysis
        print(f"\n⚙️ FEATURE ANALYSIS")
        features = self.analyze_features()
        print(f"   Total Features: {features.get('total_features', 0)}")
        print(f"   Core Capabilities: {', '.join(features.get('core_capabilities', []))}")
        print(f"   Categories:")
        for cat, items in features.get('categories', {}).items():
            print(f"      - {cat}: {len(items)} features")
        
        # Insights
        print(f"\n💡 KEY INSIGHTS")
        for insight in self.generate_insights():
            print(f"   {insight}")
        
        # Competitive analysis
        print(f"\n🏆 COMPETITIVE LANDSCAPE")
        competitive = self.generate_competitive_analysis()
        print(f"   Direct Competitors: {len(competitive['direct_competitors'])}")
        print(f"   - {', '.join(competitive['direct_competitors'][:3])}...")
        print(f"\n   Differentiation Factors:")
        for diff in competitive['differentiation']:
            print(f"   • {diff}")
        
        print("\n" + "="*70)
    
    def save_analysis(self, filename: str = None):
        """Save analysis to JSON file"""
        if not filename:
            filename = f'firecrawl_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        analysis = {
            'source_data': self.data_file,
            'pricing_analysis': self.analyze_pricing(),
            'positioning_analysis': self.analyze_positioning(),
            'feature_analysis': self.analyze_features(),
            'insights': self.generate_insights(),
            'competitive_analysis': self.generate_competitive_analysis(),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {filename}")
        return filename


def main():
    """Main entry point"""
    print("="*70)
    print("Firecrawl Analyzer")
    print("="*70)
    
    analyzer = FirecrawlAnalyzer()
    
    try:
        # Find and load latest data file
        data_file = analyzer.find_latest_data_file()
        analyzer.load_data(data_file)
        
        # Run analysis
        analyzer.print_analysis()
        
        # Save analysis
        analyzer.save_analysis()
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease run firecrawl_scraper.py first to collect data.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
