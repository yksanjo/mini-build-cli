#!/usr/bin/env python3
"""
Enhanced Music Club Scraper with Google Search
Uses Google to find actual club websites before scraping
"""

import sys
import os
import time
import json
from typing import List, Optional
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from music_club_scraper import MusicClubScraper, ClubContact

class EnhancedMusicClubScraper(MusicClubScraper):
    """Enhanced scraper that uses Google search to find club websites"""
    
    def __init__(self, use_google: bool = True, google_delay: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.use_google = use_google
        self.google_delay = google_delay
        
    def google_search_club(self, club_name: str, university: str) -> Optional[str]:
        """Use Google search to find club website"""
        if not self.use_google:
            return None
            
        try:
            from googlesearch import search
            
            # Create search queries
            queries = [
                f'"{club_name}" "{university}" website',
                f'"{club_name}" {university} club',
                f'{university} "{club_name.split()[-2]}" club',  # Use key words from club name
                f'{university} student organization "{club_name}"',
            ]
            
            print(f"  Searching Google for: {club_name}")
            
            for query in queries:
                try:
                    # Search with small number of results
                    for url in search(query, num_results=3, advanced=True):
                        # Check if it looks like a university/club page
                        if any(domain in url.url.lower() for domain in ['.edu', university.lower().replace(' ', '')]):
                            print(f"    Found: {url.url}")
                            time.sleep(self.google_delay)
                            return url.url
                except Exception as e:
                    print(f"    Google search error: {e}")
                    continue
                    
                time.sleep(self.google_delay)
                
        except ImportError:
            print("  Google search not available. Install: pip install googlesearch-python")
        except Exception as e:
            print(f"  Google search failed: {e}")
            
        return None
    
    def process_club_enhanced(self, name: str, university: str, known_url: str = None) -> ClubContact:
        """Enhanced club processing with Google search"""
        print(f"\nProcessing: {name} at {university}")
        
        # Start with club contact object
        club = ClubContact(name=name, university=university)
        
        # If URL is provided, use it
        if known_url:
            urls_to_try = [known_url]
        else:
            # First try Google search
            google_url = self.google_search_club(name, university)
            if google_url:
                urls_to_try = [google_url]
            else:
                # Fall back to URL generation
                urls_to_try = self.search_club_websites(name, university)
        
        # Try each URL
        for url in urls_to_try:
            print(f"  Trying URL: {url}")
            result = self.scrape_website(url)
            
            if result['success']:
                club.website = url
                club.emails = result['emails']
                club.social_media = result['social_media']
                club.contact_page = result['contact_page']
                club.status = 'found' if club.emails or club.social_media else 'pending'
                
                # Show results
                if club.emails:
                    print(f"    ✓ Found {len(club.emails)} email(s)")
                    for email in club.emails[:2]:  # Show first 2
                        print(f"      • {email}")
                if club.social_media:
                    print(f"    ✓ Found {len(club.social_media)} social link(s)")
                    for platform in list(club.social_media.keys())[:3]:  # Show first 3
                        print(f"      • {platform}")
                break
            
            # Add delay between attempts
            time.sleep(self.delay)
        
        # If no website found, mark as pending for manual search
        if not club.website and not known_url:
            club.status = 'pending_manual'
            print(f"  ✗ Could not find website")
        
        self.results.append(club)
        return club

def main():
    """Main enhanced scraper function"""
    print("=" * 80)
    print("ENHANCED MUSIC CLUB SCRAPER WITH GOOGLE SEARCH")
    print("=" * 80)
    print()
    
    # Initialize enhanced scraper
    scraper = EnhancedMusicClubScraper(
        delay=2.0,
        use_google=True,
        google_delay=3.0  # Longer delay for Google searches
    )
    
    # Test with a few clubs
    test_clubs = [
        # Try with some clubs that might have more visible online presence
        ("UCLA Electronic Music Collective", "UCLA"),
        ("Stanford Music Production Club", "Stanford University"),
        ("MIT Music Technology Club", "MIT"),
        ("Columbia Electronic Music Collective", "Columbia University"),
    ]
    
    print(f"Starting enhanced scraping of {len(test_clubs)} clubs...")
    print("Using Google search to find actual club websites")
    print("-" * 80)
    
    # Process each club
    for i, (club_name, university) in enumerate(test_clubs, 1):
        print(f"\n[{i}/{len(test_clubs)}]")
        club = scraper.process_club_enhanced(club_name, university)
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    json_file = f"enhanced_results_{timestamp}.json"
    csv_file = f"enhanced_results_{timestamp}.csv"
    
    # Save as JSON
    data = [club.__dict__ for club in scraper.results]
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Save as CSV
    import csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'University', 'Website', 'Emails', 'Social Media', 'Status'])
        
        for club in scraper.results:
            writer.writerow([
                club.name,
                club.university,
                club.website,
                '; '.join(club.emails),
                json.dumps(club.social_media),
                club.status
            ])
    
    # Summary
    print("\n" + "=" * 80)
    print("ENHANCED SCRAPING COMPLETE")
    print("=" * 80)
    
    total_clubs = len(scraper.results)
    clubs_with_emails = sum(1 for c in scraper.results if c.emails)
    clubs_with_social = sum(1 for c in scraper.results if c.social_media)
    total_emails = sum(len(c.emails) for c in scraper.results)
    
    print(f"Total clubs processed: {total_clubs}")
    print(f"Clubs with email addresses: {clubs_with_emails}")
    print(f"Clubs with social media: {clubs_with_social}")
    print(f"Total email addresses found: {total_emails}")
    print()
    print(f"Results saved to:")
    print(f"  • JSON: {json_file}")
    print(f"  • CSV: {csv_file}")
    
    # Show what we found
    if total_emails > 0:
        print("\nEmail addresses found:")
        all_emails = []
        for club in scraper.results:
            if club.emails:
                print(f"\n{club.name}:")
                for email in club.emails:
                    print(f"  • {email}")
                    all_emails.append(email)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS FOR OUTREACH")
    print("=" * 80)
    print("1. Review collected emails and social media links")
    print("2. Use outreach template from QUICK_START_GUIDE.md")
    print("3. Personalize emails with club/university names")
    print("4. Schedule emails for optimal response times")
    print("5. Track responses and follow up after 5-7 days")

if __name__ == "__main__":
    main()