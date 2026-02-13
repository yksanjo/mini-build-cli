#!/usr/bin/env python3
"""
Test script for Music Club Scraper
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from music_club_scraper import MusicClubScraper, ClubContact

def test_email_extraction():
    """Test email extraction functionality"""
    print("Testing email extraction...")
    
    scraper = MusicClubScraper()
    
    # Test text with emails
    test_text = """
    Contact us at: president@musicclub.usc.edu
    Or email: info.music@berklee.edu
    Also: contact@nyu-music-tech.org
    Invalid: not-an-email, user@localhost
    """
    
    emails = scraper.extract_emails(test_text)
    print(f"Found emails: {emails}")
    
    expected = ['president@musicclub.usc.edu', 'info.music@berklee.edu', 'contact@nyu-music-tech.org']
    
    if set(emails) == set(expected):
        print("✓ Email extraction test passed!")
        return True
    else:
        print(f"✗ Email extraction test failed. Expected {expected}, got {emails}")
        return False

def test_social_media_extraction():
    """Test social media link extraction"""
    print("\nTesting social media extraction...")
    
    from bs4 import BeautifulSoup
    
    # Create test HTML
    html = """
    <html>
        <body>
            <a href="https://instagram.com/usc_music">Instagram</a>
            <a href="https://facebook.com/berkleemusic">Facebook</a>
            <a href="https://twitter.com/nyumusic">Twitter</a>
            <a href="https://linkedin.com/company/ucla-music">LinkedIn</a>
            <a href="/about">Not social</a>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    scraper = MusicClubScraper()
    
    social = scraper.extract_social_media(soup, "https://example.com")
    print(f"Found social media: {social}")
    
    expected_platforms = ['instagram', 'facebook', 'twitter', 'linkedin']
    
    if all(platform in social for platform in expected_platforms):
        print("✓ Social media extraction test passed!")
        return True
    else:
        print(f"✗ Social media extraction test failed. Missing platforms.")
        return False

def test_club_contact_class():
    """Test ClubContact dataclass"""
    print("\nTesting ClubContact class...")
    
    club = ClubContact(
        name="Test Club",
        university="Test University",
        website="https://test.edu/club",
        emails=["test@test.edu", "president@test.edu"],
        social_media={"instagram": "https://instagram.com/test"},
        status="found"
    )
    
    print(f"Club created: {club.name} at {club.university}")
    print(f"Emails: {club.emails}")
    print(f"Social: {club.social_media}")
    
    if (club.name == "Test Club" and 
        club.university == "Test University" and
        len(club.emails) == 2 and
        "instagram" in club.social_media):
        print("✓ ClubContact test passed!")
        return True
    else:
        print("✗ ClubContact test failed")
        return False

def test_website_search_patterns():
    """Test URL generation patterns"""
    print("\nTesting website search patterns...")
    
    scraper = MusicClubScraper()
    
    urls = scraper.search_club_websites(
        "Electronic Music Collective",
        "University of California Los Angeles"
    )
    
    print(f"Generated URLs for UCLA Electronic Music Collective:")
    for url in urls[:3]:  # Show first 3
        print(f"  • {url}")
    
    if len(urls) > 0 and all('ucla' in url.lower() for url in urls):
        print("✓ URL generation test passed!")
        return True
    else:
        print("✗ URL generation test failed")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RUNNING MUSIC CLUB SCRAPER TESTS")
    print("=" * 60)
    
    tests = [
        test_email_extraction,
        test_social_media_extraction,
        test_club_contact_class,
        test_website_search_patterns,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All tests passed! Ready to run the scraper.")
        print("\nNext steps:")
        print("1. Run: python music_club_scraper.py")
        print("2. Check generated CSV/JSON files")
        print("3. Review QUICK_START_GUIDE.md for outreach tips")
    else:
        print("\n❌ Some tests failed. Please fix before running scraper.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)