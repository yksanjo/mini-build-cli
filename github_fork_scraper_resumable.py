#!/usr/bin/env python3
"""
GitHub Fork Scraper for Open Claw Project - RESUMABLE VERSION
Scrapes all users who forked from openclaw/openclaw repository
Can resume from where it left off if interrupted
"""

import requests
import json
import time
import csv
import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PROGRESS_FILE = "scraper_progress.json"
STATE_FILE = "scraper_state.json"

class GitHubForkScraper:
    """Scrape GitHub forks and analyze users with resume capability"""
    
    def __init__(self, github_token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Fork-Scraper/1.0"
        }
        
        self.github_token = github_token
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
            logger.info("✓ Using GitHub token for authenticated requests (5,000 req/hour)")
        else:
            logger.info("⚠ No token provided. Using public API (60 req/hour)")
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Target repository
        self.target_repo = "openclaw/openclaw"
        
        # AI/Agent keywords for analysis
        self.agent_keywords = [
            'agent', 'ai', 'llm', 'gpt', 'claude', 'openai', 'anthropic',
            'autonomous', 'assistant', 'bot', 'automation', 'workflow',
            'orchestration', 'multi-agent', 'swarm', 'crew', 'autogen',
            'langchain', 'llamaindex', 'haystack', 'semantic-kernel',
            'claw', 'openclaw', 'agentic', 'reasoning', 'cognitive'
        ]
        
        # State for resume
        self.state = self.load_state()
    
    def load_state(self):
        """Load previous state if exists"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                logger.info(f"✓ Found previous state. Resuming from user {state.get('last_processed_index', 0) + 1}")
                return state
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        return {
            'last_processed_index': -1,
            'processed_users': [],
            'forks_list': [],
            'started_at': datetime.now().isoformat()
        }
    
    def save_state(self):
        """Save current state for resume"""
        self.state['updated_at'] = datetime.now().isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def save_emergency_backup(self):
        """Save emergency backup before stopping"""
        backup_file = f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        logger.info(f"✓ Emergency backup saved to: {backup_file}")
        return backup_file
    
    def check_rate_limit(self):
        """Check current rate limit status"""
        url = f"{self.base_url}/rate_limit"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                core = data.get('resources', {}).get('core', {})
                remaining = core.get('remaining', 0)
                limit = core.get('limit', 0)
                reset_time = core.get('reset', 0)
                
                reset_str = datetime.fromtimestamp(reset_time).strftime('%H:%M:%S')
                
                logger.info(f"Rate limit: {remaining}/{limit} remaining. Resets at {reset_str}")
                
                if remaining < 10:
                    logger.warning(f"⚠ LOW RATE LIMIT! Only {remaining} requests left.")
                    logger.warning(f"   Will reset at {reset_str}")
                    return False, reset_time
                return True, reset_time
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
        return True, 0
    
    def make_request(self, url, params=None, max_retries=3):
        """Make HTTP request with rate limiting and resume support"""
        for attempt in range(max_retries):
            try:
                # Check rate limit before request
                has_limit, reset_time = self.check_rate_limit()
                
                if not has_limit:
                    wait_time = int(reset_time) - int(time.time()) + 10
                    if wait_time > 0:
                        logger.warning(f"⏳ Rate limit nearly exhausted. Waiting {wait_time} seconds...")
                        logger.warning(f"   You can safely Ctrl+C and resume later with: python3 github_fork_scraper_resumable.py")
                        
                        # Save state before waiting
                        self.save_state()
                        
                        try:
                            time.sleep(wait_time)
                        except KeyboardInterrupt:
                            logger.info("\n✓ Stopped by user. Progress saved. Resume anytime!")
                            self.save_emergency_backup()
                            sys.exit(0)
                
                # Make the request
                # Use longer delays to avoid secondary rate limiting
                if self.github_token:
                    time.sleep(2.0)  # 2 second delay with token (avoid 429s)
                else:
                    time.sleep(1.5)  # 1.5 second delay without token
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        wait_time = int(reset_time) - int(time.time()) + 10
                        if wait_time > 0:
                            logger.warning(f"⏳ Rate limit hit. Waiting {wait_time:.0f} seconds...")
                            logger.warning(f"   (Ctrl+C to stop and resume later)")
                            
                            # Save state before waiting
                            self.save_state()
                            
                            try:
                                time.sleep(wait_time)
                            except KeyboardInterrupt:
                                logger.info("\n✓ Stopped by user. Progress saved!")
                                self.save_emergency_backup()
                                sys.exit(0)
                            return self.make_request(url, params, max_retries - 1)
                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    return None
                else:
                    logger.error(f"Request failed: {response.status_code} - {response.text[:200]}")
                    
            except KeyboardInterrupt:
                logger.info("\n✓ Interrupted by user. Saving state...")
                self.save_state()
                self.save_emergency_backup()
                raise
            except Exception as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
        return None
    
    def get_forks(self, page=1, per_page=100):
        """Get forks of the target repository"""
        url = f"{self.base_url}/repos/{self.target_repo}/forks"
        params = {
            "page": page,
            "per_page": per_page,
            "sort": "newest"
        }
        
        logger.info(f"Fetching forks (page {page})...")
        return self.make_request(url, params) or []
    
    def get_all_forks(self):
        """Get all forks of the repository (or use cached list)"""
        # If we already have forks list in state, use it
        if self.state.get('forks_list') and len(self.state['forks_list']) > 0:
            logger.info(f"✓ Using cached forks list ({len(self.state['forks_list'])} forks)")
            return self.state['forks_list']
        
        all_forks = []
        page = 1
        
        logger.info("Fetching all forks from GitHub (this may take a while)...")
        
        while True:
            forks = self.get_forks(page=page)
            if not forks:
                break
                
            all_forks.extend(forks)
            logger.info(f"  Collected {len(forks)} forks from page {page} (total: {len(all_forks)})")
            
            # Check if we got fewer forks than requested (end of pages)
            if len(forks) < 100:
                break
                
            page += 1
            
            # Save state periodically while fetching forks
            if page % 5 == 0:
                self.state['forks_list'] = all_forks
                self.save_state()
        
        logger.info(f"✓ Total forks collected: {len(all_forks)}")
        
        # Save forks list to state
        self.state['forks_list'] = all_forks
        self.save_state()
        
        return all_forks
    
    def get_user_details(self, username):
        """Get detailed user information"""
        url = f"{self.base_url}/users/{username}"
        return self.make_request(url)
    
    def analyze_user(self, user_data, fork_data):
        """Analyze user for agent-related activities"""
        # Basic user info
        user_info = {
            'login': user_data.get('login'),
            'id': user_data.get('id'),
            'avatar_url': user_data.get('avatar_url'),
            'html_url': user_data.get('html_url'),
            'type': user_data.get('type'),
            'name': user_data.get('name'),
            'company': user_data.get('company'),
            'blog': user_data.get('blog'),
            'location': user_data.get('location'),
            'email': user_data.get('email'),
            'bio': user_data.get('bio'),
            'twitter_username': user_data.get('twitter_username'),
            'public_repos': user_data.get('public_repos'),
            'followers': user_data.get('followers'),
            'following': user_data.get('following'),
            'created_at': user_data.get('created_at'),
            'updated_at': user_data.get('updated_at'),
            'fork_date': fork_data.get('created_at'),
            'fork_url': fork_data.get('html_url'),
            'agent_related': False,
            'ai_agent_keywords': []
        }
        
        # Check bio for agent keywords
        bio = (user_data.get('bio') or '').lower()
        name = (user_data.get('name') or '').lower()
        
        for keyword in self.agent_keywords:
            if keyword in bio or keyword in name:
                user_info['agent_related'] = True
                user_info['ai_agent_keywords'].append(keyword)
        
        # Get user repositories to check for agent projects
        url = f"{self.base_url}/users/{user_data.get('login')}/repos"
        params = {
            "per_page": 10,
            "sort": "updated",
            "direction": "desc"
        }
        
        repos = self.make_request(url, params) or []
        
        for repo in repos:
            repo_name = (repo.get('name') or '').lower()
            repo_desc = (repo.get('description') or '').lower()
            
            for keyword in self.agent_keywords:
                if keyword in repo_name or keyword in repo_desc:
                    user_info['agent_related'] = True
                    if keyword not in user_info['ai_agent_keywords']:
                        user_info['ai_agent_keywords'].append(keyword)
        
        # Remove duplicates
        user_info['ai_agent_keywords'] = list(set(user_info['ai_agent_keywords']))
        
        return user_info
    
    def scrape_and_analyze(self):
        """Main method to scrape and analyze all forks with resume capability"""
        logger.info(f"Starting fork scraping for {self.target_repo}")
        
        # Get all forks (or use cached)
        forks = self.get_all_forks()
        
        if not forks:
            logger.error("No forks found or error fetching forks")
            return []
        
        total_forks = len(forks)
        logger.info(f"Found {total_forks} forks. Starting user analysis...")
        
        # Get resume point
        start_index = self.state.get('last_processed_index', -1) + 1
        processed_users = self.state.get('processed_users', [])
        
        if start_index > 0:
            logger.info(f"Resuming from user {start_index + 1} of {total_forks}")
            logger.info(f"Already processed: {len(processed_users)} users")
        
        # Process remaining forks
        for i in range(start_index, total_forks):
            fork = forks[i]
            owner = fork.get('owner', {})
            username = owner.get('login')
            
            if not username:
                continue
            
            logger.info(f"[{i + 1}/{total_forks}] Processing: {username}")
            
            try:
                # Get user details
                user_data = self.get_user_details(username)
                if not user_data:
                    logger.warning(f"Could not fetch details for {username}")
                    continue
                
                # Analyze user
                user = self.analyze_user(user_data, fork)
                processed_users.append(user)
                
                # Update state
                self.state['last_processed_index'] = i
                self.state['processed_users'] = processed_users
                
                # Save progress periodically (every 5 users)
                if (i + 1) % 5 == 0:
                    self.save_state()
                    logger.info(f"  ✓ Progress saved: {i + 1}/{total_forks} users")
                
                # Log agent-related users
                if user['agent_related']:
                    logger.info(f"  🎯 AGENT USER FOUND: {username} - Keywords: {', '.join(user['ai_agent_keywords'])}")
                
            except KeyboardInterrupt:
                logger.info(f"\n✓ Stopped at user {i + 1}/{total_forks}")
                self.save_state()
                backup = self.save_emergency_backup()
                logger.info(f"✓ Resume anytime with: python3 github_fork_scraper_resumable.py")
                logger.info(f"✓ Backup saved to: {backup}")
                raise
            except Exception as e:
                logger.error(f"Error processing {username}: {e}")
                continue
        
        logger.info(f"✓ Completed analysis of {len(processed_users)} users")
        
        # Clear state after successful completion
        if os.path.exists(STATE_FILE):
            os.rename(STATE_FILE, f"{STATE_FILE}.completed")
            logger.info(f"✓ State archived. Scraping complete!")
        
        return processed_users
    
    def save_results(self, users):
        """Save results in JSON and CSV formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f"github_fork_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, default=str)
        
        logger.info(f"✓ Results saved to {json_file}")
        
        # Save as CSV
        csv_file = f"github_fork_analysis_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'login', 'name', 'company', 'location', 'email',
                'bio', 'twitter_username', 'public_repos', 'followers',
                'following', 'created_at', 'fork_date', 'agent_related',
                'ai_agent_keywords', 'html_url', 'fork_url'
            ])
            
            # Write data
            for user in users:
                writer.writerow([
                    user['login'],
                    user['name'] or '',
                    user['company'] or '',
                    user['location'] or '',
                    user['email'] or '',
                    (user['bio'] or '')[:200],
                    user['twitter_username'] or '',
                    user['public_repos'] or 0,
                    user['followers'] or 0,
                    user['following'] or 0,
                    user['created_at'] or '',
                    user['fork_date'] or '',
                    user['agent_related'],
                    ', '.join(user['ai_agent_keywords']),
                    user['html_url'],
                    user['fork_url']
                ])
        
        logger.info(f"✓ Results saved to {csv_file}")
        
        # Generate summary
        self.generate_summary(users, timestamp)
    
    def generate_summary(self, users, timestamp):
        """Generate summary report"""
        agent_users = [u for u in users if u['agent_related']]
        non_agent_users = [u for u in users if not u['agent_related']]
        
        summary = {
            'timestamp': timestamp,
            'total_users': len(users),
            'agent_related_users': len(agent_users),
            'non_agent_users': len(non_agent_users),
            'agent_percentage': (len(agent_users) / len(users) * 100) if users else 0,
            'top_keywords': self.get_top_keywords(users),
            'agent_users': [u['login'] for u in agent_users],
            'sample_agent_users': [{
                'login': u['login'],
                'name': u['name'],
                'company': u['company'],
                'keywords': u['ai_agent_keywords']
            } for u in agent_users[:10]]
        }
        
        summary_file = f"github_fork_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✓ Summary saved to {summary_file}")
        
        # Print summary to console
        print("\n" + "="*80)
        print("GITHUB FORK ANALYSIS SUMMARY")
        print("="*80)
        print(f"Repository: {self.target_repo}")
        print(f"Total users analyzed: {len(users)}")
        print(f"Agent-related users: {len(agent_users)} ({summary['agent_percentage']:.1f}%)")
        print(f"Non-agent users: {len(non_agent_users)}")
        print(f"Top keywords: {', '.join(summary['top_keywords'][:5])}")
        print("\nSample Agent Users:")
        for user in summary['sample_agent_users']:
            print(f"  • {user['login']} - {user['name'] or 'No name'} - Keywords: {', '.join(user['keywords'])}")
        print("="*80)
    
    def get_top_keywords(self, users):
        """Get most common AI/agent keywords"""
        keyword_counts = {}
        for user in users:
            for keyword in user['ai_agent_keywords']:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_keywords]

def main():
    """Main function"""
    print("="*80)
    print("GITHUB FORK SCRAPER FOR OPEN CLAW PROJECT - RESUMABLE")
    print("="*80)
    print("This tool will:")
    print("1. Scrape all users who forked from openclaw/openclaw")
    print("2. Analyze each user for AI/agent-related activities")
    print("3. Save results in JSON and CSV formats")
    print("4. Generate a summary report")
    print("")
    print("✓ PROGRESS IS SAVED AUTOMATICALLY")
    print("✓ YOU CAN STOP ANYTIME WITH Ctrl+C")
    print("✓ RESUME LATER BY RUNNING THE SAME COMMAND")
    print("="*80)
    
    # Check for existing state
    if os.path.exists(STATE_FILE):
        print(f"\n📁 Found previous session. Will resume from where you left off.")
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        processed = len(state.get('processed_users', []))
        total = len(state.get('forks_list', []))
        if total > 0:
            print(f"   Progress: {processed}/{total} users ({100*processed/total:.1f}%)")
    
    # Ask for GitHub token (optional)
    github_token = input("\nEnter GitHub token (optional, press Enter to skip): ").strip()
    if not github_token:
        print("⚠ No token: 60 requests/hour (~7-8 hours total)")
    else:
        print("✓ With token: 5,000 requests/hour (~1 hour total)")
    
    # Initialize scraper
    scraper = GitHubForkScraper(github_token=github_token if github_token else None)
    
    # Start scraping
    print("\n" + "="*80)
    print("STARTING SCRAPING PROCESS...")
    print("="*80)
    print("\nTIP: Press Ctrl+C anytime to stop. Your progress will be saved!")
    print("")
    
    try:
        users = scraper.scrape_and_analyze()
        
        if users:
            # Save results
            scraper.save_results(users)
            print("\n" + "="*80)
            print("✓ SCRAPING COMPLETED SUCCESSFULLY!")
            print("="*80)
        else:
            print("\nNo users found or error during scraping.")
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("✓ STOPPED BY USER")
        print("="*80)
        print("\nYour progress has been saved!")
        print(f"State file: {STATE_FILE}")
        print("\nTo resume, just run:")
        print("  python3 github_fork_scraper_resumable.py")
        print("="*80)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        scraper.save_state()
        scraper.save_emergency_backup()
        raise

if __name__ == "__main__":
    main()
