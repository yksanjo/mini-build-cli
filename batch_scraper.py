#!/usr/bin/env python3
"""
Batch Music Club Scraper
Process large lists of clubs with progress tracking and resume capability
"""

import json
import csv
import time
from datetime import datetime
from typing import List, Tuple
from music_club_scraper import MusicClubScraper, ClubContact

def load_club_list(filename: str = "club_list.csv") -> List[Tuple[str, str, str]]:
    """Load club list from CSV file"""
    clubs = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if exists
            
            for row in reader:
                if len(row) >= 2:
                    name = row[0].strip()
                    university = row[1].strip()
                    url = row[2].strip() if len(row) > 2 else ""
                    clubs.append((name, university, url))
        
        print(f"Loaded {len(clubs)} clubs from {filename}")
        return clubs
        
    except FileNotFoundError:
        print(f"Club list file '{filename}' not found.")
        print("Creating sample club list...")
        
        # Create sample club list
        sample_clubs = [
            ("USC Thornton Electronic Production & Design", "USC", ""),
            ("Berklee Electronic Production & Design Club", "Berklee College of Music", ""),
            ("NYU Clive Davis Music Business Club", "NYU", ""),
            ("NYU Music Technology Club", "NYU", ""),
            ("UCLA Electronic Music Collective", "UCLA", ""),
        ]
        
        # Save sample
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Club Name", "University", "Known URL"])
            for club in sample_clubs:
                writer.writerow(club)
        
        print(f"Created sample club list with {len(sample_clubs)} clubs")
        return sample_clubs

def load_progress(filename: str = "scraping_progress.json") -> dict:
    """Load scraping progress"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "started": datetime.now().isoformat(),
            "completed": [],
            "failed": [],
            "pending": [],
            "total": 0
        }

def save_progress(progress: dict, filename: str = "scraping_progress.json"):
    """Save scraping progress"""
    progress["last_updated"] = datetime.now().isoformat()
    with open(filename, 'w') as f:
        json.dump(progress, f, indent=2)

def batch_process_clubs(
    clubs: List[Tuple[str, str, str]],
    batch_size: int = 10,
    delay_between_batches: int = 30,
    resume: bool = True
):
    """Process clubs in batches with progress tracking"""
    
    # Load progress if resuming
    progress = load_progress()
    
    # Filter out already completed clubs if resuming
    if resume and progress["completed"]:
        completed_set = set(progress["completed"])
        clubs = [c for c in clubs if c[0] not in completed_set]
        print(f"Resuming from previous session. {len(clubs)} clubs remaining.")
    
    total_clubs = len(clubs)
    progress["total"] = total_clubs
    
    print(f"\nStarting batch processing of {total_clubs} clubs")
    print(f"Batch size: {batch_size}")
    print(f"Delay between batches: {delay_between_batches} seconds")
    print("-" * 60)
    
    # Initialize scraper
    scraper = MusicClubScraper(delay=2.0)
    
    # Process in batches
    for batch_start in range(0, total_clubs, batch_size):
        batch_end = min(batch_start + batch_size, total_clubs)
        batch = clubs[batch_start:batch_end]
        
        print(f"\nProcessing batch {batch_start//batch_size + 1}/{(total_clubs + batch_size - 1)//batch_size}")
        print(f"Clubs {batch_start + 1} to {batch_end} of {total_clubs}")
        print("-" * 40)
        
        batch_results = []
        
        for i, (name, university, url) in enumerate(batch, 1):
            print(f"[{i}/{len(batch)}] {name}")
            
            try:
                # Process club
                club = scraper.process_club(name, university, url if url else None)
                batch_results.append(club)
                
                # Update progress
                progress["completed"].append(name)
                
                # Show quick results
                if club.emails:
                    print(f"   ✓ {len(club.emails)} email(s) found")
                if club.social_media:
                    print(f"   ✓ {len(club.social_media)} social link(s) found")
                if not club.emails and not club.social_media:
                    print(f"   ✗ No contact info found")
                    
            except Exception as e:
                print(f"   ✗ Error: {e}")
                progress["failed"].append({
                    "name": name,
                    "university": university,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Save progress after each club
            save_progress(progress)
        
        # Save batch results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_file = f"batch_results_{timestamp}.json"
        
        batch_data = [club.__dict__ for club in batch_results]
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f, indent=2)
        
        print(f"\nBatch results saved to: {batch_file}")
        
        # Delay between batches (except last batch)
        if batch_end < total_clubs:
            print(f"\nWaiting {delay_between_batches} seconds before next batch...")
            time.sleep(delay_between_batches)
    
    # Final save
    save_progress(progress)
    
    # Combine all results
    all_results_file = f"all_club_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    all_data = [club.__dict__ for club in scraper.results]
    
    with open(all_results_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Also save as CSV
    csv_file = all_results_file.replace('.json', '.csv')
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
    
    return scraper.results, all_results_file, csv_file

def generate_summary(results: List[ClubContact]):
    """Generate summary report"""
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    
    total_clubs = len(results)
    clubs_with_emails = sum(1 for c in results if c.emails)
    clubs_with_social = sum(1 for c in results if c.social_media)
    total_emails = sum(len(c.emails) for c in results)
    
    print(f"Total clubs processed: {total_clubs}")
    print(f"Clubs with email addresses: {clubs_with_emails} ({clubs_with_emails/total_clubs*100:.1f}%)")
    print(f"Clubs with social media: {clubs_with_social} ({clubs_with_social/total_clubs*100:.1f}%)")
    print(f"Total email addresses collected: {total_emails}")
    print(f"Average emails per club: {total_emails/total_clubs:.1f}" if total_clubs > 0 else "0")
    
    # Show top email domains
    if total_emails > 0:
        print("\nTop email domains:")
        domains = {}
        for club in results:
            for email in club.emails:
                domain = email.split('@')[-1] if '@' in email else 'unknown'
                domains[domain] = domains.get(domain, 0) + 1
        
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {domain}: {count} emails")
    
    # Show social media platforms
    platforms = {}
    for club in results:
        for platform in club.social_media.keys():
            platforms[platform] = platforms.get(platform, 0) + 1
    
    if platforms:
        print("\nSocial media platforms found:")
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True):
            print(f"  {platform}: {count} clubs")

def main():
    """Main batch processing function"""
    print("=" * 60)
    print("BATCH MUSIC CLUB SCRAPER")
    print("=" * 60)
    
    # Configuration
    CLUB_LIST_FILE = "club_list.csv"
    BATCH_SIZE = 5  # Clubs per batch
    BATCH_DELAY = 20  # Seconds between batches
    RESUME = True  # Resume from previous session
    
    # Load club list
    clubs = load_club_list(CLUB_LIST_FILE)
    
    if not clubs:
        print("No clubs to process. Exiting.")
        return
    
    # Confirm before starting
    print(f"\nReady to process {len(clubs)} clubs.")
    print(f"Configuration:")
    print(f"  • Batch size: {BATCH_SIZE} clubs")
    print(f"  • Delay between batches: {BATCH_DELAY} seconds")
    print(f"  • Resume mode: {'ON' if RESUME else 'OFF'}")
    
    input("\nPress Enter to start scraping (Ctrl+C to cancel)...")
    
    try:
        # Process clubs
        results, json_file, csv_file = batch_process_clubs(
            clubs, 
            batch_size=BATCH_SIZE,
            delay_between_batches=BATCH_DELAY,
            resume=RESUME
        )
        
        # Generate summary
        generate_summary(results)
        
        print(f"\nResults saved to:")
        print(f"  • JSON: {json_file}")
        print(f"  • CSV: {csv_file}")
        print(f"  • Progress: scraping_progress.json")
        
        print("\n✅ Batch processing complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user.")
        print("Progress has been saved. Run again to resume.")
    except Exception as e:
        print(f"\n❌ Error during batch processing: {e}")
        print("Check scraping_progress.json for completed work.")

if __name__ == "__main__":
    main()