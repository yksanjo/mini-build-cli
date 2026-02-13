#!/usr/bin/env python3
"""
Demonstration of Music Club Scraper
Shows basic functionality without actual web requests
"""

import re
from bs4 import BeautifulSoup

def demonstrate_email_extraction():
    """Show how email extraction works"""
    print("=" * 60)
    print("DEMONSTRATION: Email Extraction")
    print("=" * 60)
    
    # Sample text that might be on a club website
    sample_text = """
    <div class="contact-info">
        <h3>Contact Us</h3>
        <p>Club President: <a href="mailto:president.music@usc.edu">president.music@usc.edu</a></p>
        <p>Treasurer: treasurer.epd@berklee.edu</p>
        <p>General Inquiries: contact@nyu-music-tech.org</p>
        <p>Faculty Advisor: prof.smith@columbia.edu</p>
        <p>Not an email: just text, user@localhost, @twitterhandle</p>
    </div>
    """
    
    print("Sample HTML from club website:")
    print(sample_text)
    print("\nExtracted emails:")
    
    # Email regex pattern (same as in main scraper)
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, sample_text)
    
    for email in emails:
        print(f"  • {email}")
    
    print(f"\nTotal emails found: {len(emails)}")
    return emails

def demonstrate_social_media_extraction():
    """Show how social media extraction works"""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Social Media Extraction")
    print("=" * 60)
    
    # Sample HTML with social media links
    sample_html = """
    <footer>
        <div class="social-links">
            <a href="https://instagram.com/usc_music" class="social-link">
                <span>Follow us on Instagram</span>
            </a>
            <a href="https://facebook.com/berkleemusicclub">
                <img src="/facebook-icon.png" alt="Facebook">
            </a>
            <a href="https://twitter.com/nyumusictech">
                Twitter Updates
            </a>
            <a href="https://linkedin.com/company/ucla-emc">
                LinkedIn
            </a>
            <a href="https://youtube.com/c/columbiamusic">
                YouTube Channel
            </a>
            <a href="/about">About Us</a>
            <a href="mailto:contact@club.edu">Email</a>
        </div>
    </footer>
    """
    
    print("Sample HTML with social links:")
    print(sample_html)
    
    # Parse HTML
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Social media platforms to look for
    social_platforms = {
        'instagram': ['instagram.com'],
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com'],
        'youtube': ['youtube.com', 'youtu.be'],
    }
    
    print("\nExtracted social media links:")
    social_links = {}
    
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        
        for platform, domains in social_platforms.items():
            if any(domain in href for domain in domains):
                if platform not in social_links:
                    social_links[platform] = href
                    print(f"  • {platform}: {href}")
                break
    
    print(f"\nTotal social platforms found: {len(social_links)}")
    return social_links

def demonstrate_url_generation():
    """Show how URL generation works for university clubs"""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Smart URL Generation")
    print("=" * 60)
    
    test_clubs = [
        ("Electronic Music Collective", "University of California Los Angeles"),
        ("Music Production Club", "Stanford University"),
        ("Audio Engineering Society", "Georgia Tech"),
    ]
    
    print("Generating potential website URLs for clubs:")
    
    for club_name, university in test_clubs:
        print(f"\n{club_name} at {university}:")
        
        # Clean university name for URL
        uni_clean = university.lower().replace(' ', '').replace('.', '')
        club_clean = club_name.lower().replace(' ', '-')
        
        # Generate potential URLs
        urls = [
            f"https://{uni_clean}.edu/music/{club_clean}",
            f"https://music.{uni_clean}.edu/student-organizations/{club_clean}",
            f"https://{uni_clean}.edu/studentlife/clubs/{club_clean}",
        ]
        
        for url in urls:
            print(f"  • {url}")
    
    return test_clubs

def demonstrate_data_structure():
    """Show the data structure for collected contacts"""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Data Structure")
    print("=" * 60)
    
    # Simulated collected data
    club_data = {
        "name": "USC Thornton Electronic Production & Design",
        "university": "USC",
        "website": "https://music.usc.edu/student-organizations/epd",
        "emails": [
            "president.epd@usc.edu",
            "treasurer.music@usc.edu",
            "faculty.advisor@thornton.usc.edu"
        ],
        "social_media": {
            "instagram": "https://instagram.com/usc_epd",
            "facebook": "https://facebook.com/uscepdclub",
            "twitter": "https://twitter.com/usc_epd"
        },
        "contact_page": "https://music.usc.edu/contact-epd",
        "status": "found",
        "last_updated": "2024-01-30T18:30:00"
    }
    
    print("Example of collected data structure:")
    print(json.dumps(club_data, indent=2))
    
    print("\nThis data would be saved as:")
    print("  • JSON: For programmatic use")
    print("  • CSV: For spreadsheet analysis")
    print("  • Database: For large-scale tracking")
    
    return club_data

def demonstrate_outreach_template():
    """Show outreach email template"""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Outreach Template")
    print("=" * 60)
    
    template = """Subject: Invitation to AI Music Production Discord Community

Dear {contact_name},

I hope this message finds you well! I'm reaching out from {your_organization}, 
an AI music production community on Discord with {member_count}+ members.

I came across your {club_name} at {university} and was impressed by your 
work in music production/technology. Our community brings together music 
producers, audio engineers, and AI enthusiasts to:

1. Explore AI music tools and techniques
2. Participate in monthly production challenges
3. Attend virtual workshops and networking events
4. Collaborate on projects with other universities

As a special offer for student clubs, we'd be happy to:
- Host a free virtual workshop for your members
- Feature your club's work in our community showcase
- Provide access to AI music tools and resources

Would you be open to sharing our Discord invite link with your members?

Join here: {discord_invite_link}

Looking forward to connecting!

Best regards,
{your_name}
{your_title}
{your_organization}"""

    print("Personalized outreach email template:")
    print(template)
    
    print("\nTemplate variables to fill:")
    print("  • {contact_name}: Club president/officer name")
    print("  • {club_name}: Name of the music club")
    print("  • {university}: University name")
    print("  • {member_count}: Your Discord member count")
    print("  • {discord_invite_link}: Your Discord invite URL")
    print("  • {your_name}, {your_title}, {your_organization}: Your info")
    
    return template

import json

def main():
    """Run all demonstrations"""
    print("\n" + "=" * 60)
    print("MUSIC CLUB SCRAPER - FUNCTIONAL DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo shows how the scraper works without making actual web requests.")
    print("All examples use simulated data to demonstrate the concepts.\n")
    
    # Run demonstrations
    emails = demonstrate_email_extraction()
    social_links = demonstrate_social_media_extraction()
    test_clubs = demonstrate_url_generation()
    club_data = demonstrate_data_structure()
    template = demonstrate_outreach_template()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: What the Scraper Does")
    print("=" * 60)
    
    print("\n1. EMAIL EXTRACTION")
    print(f"   • Uses regex patterns to find emails in HTML")
    print(f"   • Example: Found {len(emails)} emails in sample text")
    
    print("\n2. SOCIAL MEDIA EXTRACTION")
    print(f"   • Parses HTML for social media platform links")
    print(f"   • Example: Found {len(social_links)} social platforms")
    
    print("\n3. URL GENERATION")
    print(f"   • Creates potential website URLs from club/university names")
    print(f"   • Example: Generated URLs for {len(test_clubs)} test clubs")
    
    print("\n4. DATA STRUCTURE")
    print("   • Organizes collected data in consistent format")
    print("   • Includes emails, social links, metadata")
    
    print("\n5. OUTREACH TEMPLATE")
    print("   • Provides personalized email template for outreach")
    print("   • Variables automatically filled from scraped data")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    print("\nTo run the actual scraper:")
    print("1. Install requirements: pip install -r requirements_music_scraper.txt")
    print("2. Test: python test_scraper.py")
    print("3. Run basic scraper: python music_club_scraper.py")
    print("4. Scale up: python batch_scraper.py")
    
    print("\nFor detailed instructions, see:")
    print("  • QUICK_START_GUIDE.md - Step-by-step guide")
    print("  • music_club_scraping_strategy.md - Comprehensive strategy")
    print("  • README.md - Complete documentation")

if __name__ == "__main__":
    main()