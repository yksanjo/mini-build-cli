#!/usr/bin/env python3
"""
GitHub Fork Scraper for Open Claw Project
Scrapes all users who forked from openclaw/openclaw repository
"""

import requests
import json
import time
import csv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubForkScraper:
    """Scrape GitHub forks and analyze users"""
    
    def __init__(self, github_token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Fork-Scraper/1.0"
        }
        
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
            logger.info("Using GitHub token for authenticated requests")
        
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
    
    def make_request(self, url, params=None):
        """Make HTTP request with rate limiting"""
        try:
            time.sleep(1)  # Rate limit delay
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                # Rate limit hit
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    wait_time = int(reset_time) - time.time() + 10
                    if wait_time > 0:
                        logger.warning(f"Rate limit hit. Waiting {wait_time:.0f} seconds...")
                        time.sleep(wait_time)
                        return self.make_request(url, params)
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
            else:
                logger.error(f"Request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            
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
        """Get all forks of the repository"""
        all_forks = []
        page = 1
        
        while True:
            forks = self.get_forks(page=page)
            if not forks:
                break
                
            all_forks.extend(forks)
            logger.info(f"Collected {len(forks)} forks from page {page}")
            
            # Check if we got fewer forks than requested (end of pages)
            if len(forks) < 100:
                break
                
            page += 1
            
        logger.info(f"Total forks collected: {len(all_forks)}")
        return all_forks
    
    def get_user_details(self, username):
        """Get detailed user information"""
        url = f"{self.base_url}/users/{username}"
        logger.info(f"Fetching details for user: {username}")
        return self.make_request(url)
    
    def analyze_user(self, user_data, fork_data):
        """Analyze user for agent-related activities"""
        logger.info(f"Analyzing user: {user_data.get('login')}")
        
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
                        user_info['ai_agent_keywords'].append(keykeyword)
        
        # Remove duplicates
        user_info['ai_agent_keywords'] = list(set(user_info['ai_agent_keywords']))
        
        logger.info(f"User {user_info['login']} analysis complete. Agent related: {user_info['agent_related']}")
        return user_info
    
    def scrape_and_analyze(self):
        """Main method to scrape and analyze all forks"""
        logger.info(f"Starting fork scraping for {self.target_repo}")
        
        # Get all forks
        forks = self.get_all_forks()
        
        if not forks:
            logger.error("No forks found or error fetching forks")
            return []
        
        logger.info(f"Found {len(forks)} forks. Starting user analysis...")
        
        # Analyze each fork owner
        users = []
        for i, fork in enumerate(forks, 1):
            owner = fork.get('owner', {})
            username = owner.get('login')
            
            if not username:
                continue
                
            logger.info(f"[{i}/{len(forks)}] Processing fork from: {username}")
            
            # Get user details
            user_data = self.get_user_details(username)
            if not user_data:
                logger.warning(f"Could not fetch details for {username}")
                continue
            
            # Analyze user
            user = self.analyze_user(user_data, fork)
            users.append(user)
            
            # Save progress periodically
            if i % 5 == 0:
                self.save_progress(users, f"progress_{i}.json")
        
        logger.info(f"Completed analysis of {len(users)} users")
        return users
    
    def save_progress(self, users, filename):
        """Save progress to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, default=str)
        
        logger.info(f"Progress saved to {filename}")
    
    def save_results(self, users):
        """Save results in JSON and CSV formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f"github_fork_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, default=str)
        
        logger.info(f"Results saved to {json_file}")
        
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
        
        logger.info(f"Results saved to {csv_file}")
        
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
            } for u in agent_users[:10]]  # First 10 agent users
        }
        
        summary_file = f"github_fork_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary saved to {summary_file}")
        
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
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_keywords]

def main():
    """Main function"""
    print("="*80)
    print("GITHUB FORK SCRAPER FOR OPEN CLAW PROJECT")
    print("="*80)
    print("This tool will:")
    print("1. Scrape all users who forked from openclaw/openclaw")
    print("2. Analyze each user for AI/agent-related activities")
    print("3. Save results in JSON and CSV formats")
    print("4. Generate a summary report")
    print("="*80)
    
    # Ask for GitHub token (optional)
    github_token = input("\nEnter GitHub token (optional, press Enter to skip): ").strip()
    if not github_token:
        print("Note: Without a token, you have lower rate limits (60 requests/hour)")
    
    # Initialize scraper
    scraper = GitHubForkScraper(github_token=github_token if github_token else None)
    
    # Start scraping
    print("\nStarting scraping process...")
    users = scraper.scrape_and_analyze()
    
    if users:
        # Save results
        scraper.save_results(users)
        print("\nScraping completed successfully!")
    else:
        print("\nNo users found or error during scraping.")

if __name__ == "__main__":
    main()