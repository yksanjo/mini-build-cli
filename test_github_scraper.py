#!/usr/bin/env python3
"""
Quick test to verify GitHub API access and Open Claw repository
"""

import requests
import json

def test_github_api():
    """Test GitHub API access"""
    print("Testing GitHub API access...")
    
    # Test the Open Claw repository
    url = "https://api.github.com/repos/openclaw/openclaw"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Test/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            print("✓ Successfully accessed Open Claw repository")
            print(f"  Repository: {repo_data.get('full_name')}")
            print(f"  Description: {repo_data.get('description')}")
            print(f"  Stars: {repo_data.get('stargazers_count')}")
            print(f"  Forks: {repo_data.get('forks_count')}")
            print(f"  Created: {repo_data.get('created_at')}")
            print(f"  Updated: {repo_data.get('updated_at')}")
            print(f"  URL: {repo_data.get('html_url')}")
            
            # Test forks endpoint
            forks_url = "https://api.github.com/repos/openclaw/openclaw/forks?per_page=5"
            forks_response = requests.get(forks_url, headers=headers)
            
            if forks_response.status_code == 200:
                forks = forks_response.json()
                print(f"\n✓ Found {len(forks)} recent forks")
                print("  Recent forks:")
                for i, fork in enumerate(forks, 1):
                    owner = fork.get('owner', {})
                    print(f"    {i}. {owner.get('login')} - {fork.get('created_at')}")
                
                # Test user endpoint for first fork owner
                if forks:
                    first_owner = forks[0].get('owner', {})
                    user_url = f"https://api.github.com/users/{first_owner.get('login')}"
                    user_response = requests.get(user_url, headers=headers)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        print(f"\n✓ Successfully accessed user data for {first_owner.get('login')}")
                        print(f"  Name: {user_data.get('name')}")
                        print(f"  Company: {user_data.get('company')}")
                        print(f"  Location: {user_data.get('location')}")
                        print(f"  Public repos: {user_data.get('public_repos')}")
                        print(f"  Followers: {user_data.get('followers')}")
            
            return True
            
        else:
            print(f"✗ Failed to access repository: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_rate_limits():
    """Check GitHub API rate limits"""
    print("\nChecking GitHub API rate limits...")
    
    url = "https://api.github.com/rate_limit"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Test/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            limits = response.json()
            core = limits.get('resources', {}).get('core', {})
            print(f"  Rate limit: {core.get('limit', 'Unknown')}")
            print(f"  Remaining: {core.get('remaining', 'Unknown')}")
            print(f"  Resets at: {core.get('reset', 'Unknown')}")
            
            if core.get('remaining', 0) < 10:
                print("  ⚠️ Warning: Low rate limit remaining!")
            return True
        else:
            print(f"✗ Failed to check rate limits: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main test function"""
    print("="*80)
    print("GITHUB API TEST FOR OPEN CLAW FORK MAPPING")
    print("="*80)
    
    # Test API access
    if test_github_api():
        print("\n✓ GitHub API access test PASSED")
    else:
        print("\n✗ GitHub API access test FAILED")
        print("  Please check your internet connection and GitHub status.")
    
    # Check rate limits
    check_rate_limits()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Run 'python github_fork_scraper.py' to start full scraping")
    print("2. Consider getting a GitHub token for higher rate limits")
    print("3. Monitor progress in the generated JSON/CSV files")
    print("="*80)

if __name__ == "__main__":
    main()