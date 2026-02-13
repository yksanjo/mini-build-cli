#!/usr/bin/env python3
"""
Check scraper status and manage resume
"""

import json
import os
from datetime import datetime

STATE_FILE = "scraper_state.json"

def format_time(iso_string):
    """Format ISO time string"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string

def check_status():
    """Check current scraper status"""
    print("="*80)
    print("GITHUB FORK SCRAPER STATUS CHECK")
    print("="*80)
    
    if not os.path.exists(STATE_FILE):
        print("\n✗ No previous session found.")
        print("\nTo start fresh, run:")
        print("  python3 github_fork_scraper_resumable.py")
        return
    
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        processed = state.get('processed_users', [])
        forks_list = state.get('forks_list', [])
        last_index = state.get('last_processed_index', -1)
        started = state.get('started_at', 'Unknown')
        updated = state.get('updated_at', 'Unknown')
        
        total_forks = len(forks_list)
        processed_count = len(processed)
        
        print(f"\n📊 Session Status:")
        print(f"   Started: {format_time(started)}")
        print(f"   Last Update: {format_time(updated)}")
        print("")
        print(f"📈 Progress:")
        print(f"   Forks in list: {total_forks}")
        print(f"   Users processed: {processed_count}")
        
        if total_forks > 0:
            percent = (processed_count / total_forks) * 100
            remaining = total_forks - processed_count
            print(f"   Complete: {percent:.1f}%")
            print(f"   Remaining: {remaining} users")
            
            # Estimate time remaining
            if remaining > 0:
                # Rough estimate: 2 API calls per user, ~1 second per call with token
                est_seconds = remaining * 2  # With token
                est_hours = est_seconds / 3600
                print(f"   Est. time remaining: ~{est_hours:.1f} hours (with token)")
                print(f"                        ~{est_hours * 5:.1f} hours (without token)")
        
        # Show agent users found so far
        agent_users = [u for u in processed if u.get('agent_related')]
        if agent_users:
            print(f"\n🎯 Agent Users Found: {len(agent_users)}")
            print("   Recent finds:")
            for user in agent_users[-5:]:  # Show last 5
                keywords = ', '.join(user.get('ai_agent_keywords', [])[:3])
                print(f"   • {user['login']}: {keywords}")
        
        print("\n" + "="*80)
        print("OPTIONS:")
        print("="*80)
        print("1. Resume scraping:")
        print("   python3 github_fork_scraper_resumable.py")
        print("")
        print("2. View full processed list:")
        print("   python3 check_scraper_status.py --list")
        print("")
        print("3. Export current progress to CSV:")
        print("   python3 check_scraper_status.py --export")
        print("")
        print("4. Reset and start over:")
        print(f"   rm {STATE_FILE}")
        print("   python3 github_fork_scraper_resumable.py")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ Error reading state file: {e}")
        print("The state file may be corrupted. You can:")
        print(f"  rm {STATE_FILE}")
        print("  python3 github_fork_scraper_resumable.py")

def list_users():
    """List all processed users"""
    if not os.path.exists(STATE_FILE):
        print("No state file found.")
        return
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    users = state.get('processed_users', [])
    
    print(f"\nTotal processed users: {len(users)}\n")
    print(f"{'#':<5} {'Username':<20} {'Agent?':<8} {'Keywords'}")
    print("-"*80)
    
    for i, user in enumerate(users, 1):
        is_agent = "YES" if user.get('agent_related') else "no"
        keywords = ', '.join(user.get('ai_agent_keywords', [])[:3])
        print(f"{i:<5} {user['login']:<20} {is_agent:<8} {keywords}")

def export_progress():
    """Export current progress to CSV"""
    import csv
    
    if not os.path.exists(STATE_FILE):
        print("No state file found.")
        return
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    users = state.get('processed_users', [])
    
    if not users:
        print("No users processed yet.")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f"github_fork_progress_export_{timestamp}.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'login', 'name', 'company', 'location', 'agent_related',
            'ai_agent_keywords', 'html_url'
        ])
        
        for user in users:
            writer.writerow([
                user['login'],
                user.get('name') or '',
                user.get('company') or '',
                user.get('location') or '',
                user.get('agent_related'),
                ', '.join(user.get('ai_agent_keywords', [])),
                user.get('html_url')
            ])
    
    print(f"✓ Exported {len(users)} users to: {csv_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_users()
        elif sys.argv[1] == '--export':
            export_progress()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage:")
            print("  python3 check_scraper_status.py         # Show status")
            print("  python3 check_scraper_status.py --list  # List all users")
            print("  python3 check_scraper_status.py --export # Export to CSV")
    else:
        check_status()
