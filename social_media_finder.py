#!/usr/bin/env python3
"""
Social Media Finder for Music Clubs
Focuses on finding Instagram/Facebook profiles which often have contact info
"""

import sys
import os
import time
import json
import re
from typing import List, Dict, Optional
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from music_club_scraper import MusicClubScraper, ClubContact

class SocialMediaFinder:
    """Finds social media profiles for music clubs"""
    
    def __init__(self):
        self.scraper = MusicClubScraper(delay=1.5)
        self.results: List[ClubContact] = []
        
    def generate_social_search_terms(self, club_name: str, university: str) -> List[str]:
        """Generate search terms for social media profiles"""
        # Clean names for search
        club_clean = club_name.lower()
        uni_clean = university.lower()
        
        # Extract key words
        club_words = [w for w in club_clean.split() if w not in ['club', 'society', 'collective', 'association', 'group']]
        uni_words = [w for w in uni_clean.split() if w not in ['university', 'college', 'school', 'institute']]
        
        # Common social media handle patterns
        search_terms = []
        
        # Instagram patterns
        instagram_patterns = [
            f"{' '.join(club_words)} {uni_clean}",
            f"{' '.join(club_words[:2])} {uni_words[0] if uni_words else ''}",
            f"{club_words[0] if club_words else ''}{uni_words[0] if uni_words else ''}",
            f"{uni_words[0] if uni_words else ''}{club_words[0] if club_words else ''}",
        ]
        
        # Facebook patterns
        facebook_patterns = [
            f"{club_name} {university}",
            f"{club_name} Club",
            f"{university} {club_name.split()[-1]} Club",
        ]
        
        # Combine and clean
        all_terms = instagram_patterns + facebook_patterns
        unique_terms = []
        for term in all_terms:
            term = term.strip().lower()
            if term and term not in unique_terms:
                unique_terms.append(term)
        
        return unique_terms
    
    def search_social_media_profiles(self, club_name: str, university: str) -> Dict[str, str]:
        """Try to find social media profiles"""
        print(f"  Searching for social media profiles...")
        
        social_links = {}
        search_terms = self.generate_social_search_terms(club_name, university)
        
        # Try direct social media platform searches
        platforms = {
            'instagram': 'https://www.instagram.com/{handle}/',
            'facebook': 'https://www.facebook.com/{handle}/',
            'twitter': 'https://twitter.com/{handle}',
        }
        
        # Common handle patterns to try
        handle_patterns = []
        
        # Create potential handles
        club_key = ''.join([w[:3] for w in club_name.lower().split()[:2]])
        uni_key = ''.join([w[:3] for w in university.lower().split()[:2]])
        
        handle_patterns.extend([
            f"{club_key}{uni_key}",
            f"{uni_key}{club_key}",
            f"{club_name.lower().replace(' ', '')}",
            f"{university.lower().replace(' ', '')}{club_name.lower().split()[0]}",
        ])
        
        # Try each platform with each handle pattern
        for platform, url_pattern in platforms.items():
            for handle in handle_patterns[:3]:  # Try first 3 patterns
                handle = handle.replace('&', 'and').replace(' ', '').lower()
                test_url = url_pattern.format(handle=handle)
                
                print(f"    Trying {platform}: {test_url}")
                
                try:
                    # Just check if page exists (HEAD request)
                    response = self.scraper.session.head(test_url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        social_links[platform] = test_url
                        print(f"      ✓ Found {platform} profile")
                        break  # Found one for this platform, move to next
                except:
                    continue
                
                time.sleep(0.5)  # Small delay between attempts
        
        return social_links
    
    def find_club_contacts(self, club_name: str, university: str) -> ClubContact:
        """Find contacts for a club with focus on social media"""
        print(f"\nProcessing: {club_name}")
        print(f"University: {university}")
        
        # Start with club contact object
        club = ClubContact(name=club_name, university=university)
        
        # Step 1: Try to find social media profiles
        social_media = self.search_social_media_profiles(club_name, university)
        
        if social_media:
            club.social_media = social_media
            club.status = 'found_social'
            print(f"  ✓ Found {len(social_media)} social media profiles")
        
        # Step 2: Try university student organization directory
        uni_urls = self.scraper.search_club_websites(club_name, university)
        for url in uni_urls[:2]:  # Try first 2 URLs
            print(f"  Trying university directory: {url}")
            result = self.scraper.scrape_website(url)
            
            if result['success']:
                club.website = url
                club.emails.extend(result['emails'])
                
                # Add any new social media links
                for platform, link in result['social_media'].items():
                    if platform not in club.social_media:
                        club.social_media[platform] = link
                
                if result['contact_page']:
                    club.contact_page = result['contact_page']
                
                if club.emails or club.social_media:
                    club.status = 'found'
                
                break
        
        # Step 3: If we found social media but no emails, try to extract from social media
        if club.social_media and not club.emails:
            # For now, we'll note that emails might be in social media bios
            print(f"  Note: Check social media bios for contact info")
        
        # Remove duplicate emails
        club.emails = list(dict.fromkeys(club.emails))
        
        # Update status if we found something
        if not club.emails and not club.social_media:
            club.status = 'pending_manual'
            print(f"  ✗ No contacts found")
        elif club.emails:
            print(f"  ✓ Found {len(club.emails)} email(s)")
        elif club.social_media:
            print(f"  ✓ Found {len(club.social_media)} social media link(s)")
        
        self.results.append(club)
        return club
    
    def save_results(self, filename: str = "social_media_contacts.json"):
        """Save results to file"""
        data = [club.__dict__ for club in self.results]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nResults saved to: {filename}")
        return filename

def main():
    """Main social media finder function"""
    print("=" * 80)
    print("SOCIAL MEDIA FINDER FOR MUSIC CLUBS")
    print("=" * 80)
    print("\nFocus: Finding Instagram/Facebook profiles with contact information")
    print()
    
    # Initialize finder
    finder = SocialMediaFinder()
    
    # Test with clubs that likely have social media presence
    test_clubs = [
        # Clubs that are likely to have active social media
        ("UCLA Electronic Music Collective", "UCLA"),
        ("USC Music Production", "USC"),
        ("Berklee Electronic Music", "Berklee College of Music"),
        ("NYU Music Tech", "NYU"),
        ("UT Austin DJ Collective", "University of Texas Austin"),
    ]
    
    print(f"Searching for {len(test_clubs)} clubs...")
    print("-" * 80)
    
    # Process each club
    for i, (club_name, university) in enumerate(test_clubs, 1):
        print(f"\n[{i}/{len(test_clubs)}]")
        club = finder.find_club_contacts(club_name, university)
    
    # Save results
    json_file = finder.save_results()
    
    # Also save as CSV
    import csv
    csv_file = json_file.replace('.json', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Club Name', 'University', 'Instagram', 'Facebook', 'Twitter', 'Emails', 'Status'])
        
        for club in finder.results:
            writer.writerow([
                club.name,
                club.university,
                club.social_media.get('instagram', ''),
                club.social_media.get('facebook', ''),
                club.social_media.get('twitter', ''),
                '; '.join(club.emails),
                club.status
            ])
    
    # Summary
    print("\n" + "=" * 80)
    print("SOCIAL MEDIA SEARCH COMPLETE")
    print("=" * 80)
    
    total_clubs = len(finder.results)
    clubs_with_social = sum(1 for c in finder.results if c.social_media)
    clubs_with_emails = sum(1 for c in finder.results if c.emails)
    
    print(f"Total clubs searched: {total_clubs}")
    print(f"Clubs with social media found: {clubs_with_social}")
    print(f"Clubs with emails found: {clubs_with_emails}")
    
    # Show social media platforms found
    if clubs_with_social > 0:
        platforms = {}
        for club in finder.results:
            for platform in club.social_media.keys():
                platforms[platform] = platforms.get(platform, 0) + 1
        
        print("\nSocial media platforms found:")
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {platform}: {count} clubs")
    
    print(f"\nResults saved to:")
    print(f"  • JSON: {json_file}")
    print(f"  • CSV: {csv_file}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS FOR DISCORD OUTREACH")
    print("=" * 80)
    print("""
1. MANUAL SOCIAL MEDIA CHECK:
   • Visit found Instagram/Facebook profiles
   • Check bio sections for email/contact info
   • Look for 'Link in bio' for websites

2. DIRECT MESSAGE OUTREACH:
   • Use Instagram/Facebook messaging
   • Keep messages brief and professional
   • Offer value (free workshop, collaboration)

3. EMAIL FOLLOW-UP:
   • Use any found email addresses
   • Personalize with club/university names
   • Include Discord invite link

4. TRACK RESPONSES:
   • Create spreadsheet for tracking
   • Note which approach works best
   • Follow up after 3-5 days
    """)

if __name__ == "__main__":
    main()