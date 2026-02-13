#!/usr/bin/env python3
"""
GitHub Repository Cleanup Tool
Identifies and helps delete:
1. Forked repos not running locally
2. Cloudflare/bot copies that aren't active
3. GitHub-only repos that are duplicates or unused
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Set

# Load GitHub inventory
with open('github_repos_inventory.json', 'r') as f:
    GITHUB_REPOS = json.load(f)

# Local directories to check
LOCAL_DIRS = set()
for item in os.listdir('.'):
    if os.path.isdir(item) and not item.startswith('.'):
        git_dir = os.path.join(item, '.git')
        if os.path.exists(git_dir):
            LOCAL_DIRS.add(item)

# Define patterns for repos to potentially delete
BOT_KEYWORDS = [
    'bot', 'claw', 'moltworker', 'agent-', '-agent', 'chatbot', 
    'openclaw', 'clawdbot', 'clawd'
]

CLOUDFLARE_KEYWORDS = [
    'cloudflare', 'worker', 'moltworker'
]

FORK_KEEP_LIST = {
    'ddsp-piano',  # Has 1 star, seems intentional
}

LOCAL_ACTIVE_PROJECTS = {
    # These are projects you confirmed are running locally
    'clawd',
    'clawdbot-deepseek', 
    'clawdbot-launchpad',
    'moltworker',
    'moltworker-cloudflare',
    'moltworker-simplified',
    'openclawsandbox',
}

def categorize_repos():
    """Categorize all GitHub repos for cleanup decisions"""
    
    categories = {
        'forks_not_local': [],
        'bot_repos_not_local': [],
        'github_only_unused': [],
        'keep_recommended': [],
        'needs_review': []
    }
    
    github_repo_names = {r['name'] for r in GITHUB_REPOS}
    
    for repo in GITHUB_REPOS:
        name = repo['name']
        is_fork = repo.get('is_fork', False)
        is_local = name in LOCAL_DIRS
        stars = repo.get('stars', 0)
        desc = (repo.get('description') or '').lower()
        
        # Determine if it's a bot/claw related repo
        is_bot_related = any(k in name.lower() for k in BOT_KEYWORDS)
        is_cloudflare = any(k in name.lower() for k in CLOUDFLARE_KEYWORDS)
        
        repo_info = {
            'name': name,
            'full_name': repo['full_name'],
            'url': repo['url'],
            'is_fork': is_fork,
            'is_local': is_local,
            'stars': stars,
            'description': repo.get('description'),
            'updated_at': repo.get('updated_at'),
            'is_bot_related': is_bot_related,
            'is_cloudflare': is_cloudflare
        }
        
        # Decision logic
        if is_fork:
            if name in FORK_KEEP_LIST or is_local:
                categories['keep_recommended'].append(repo_info)
            else:
                categories['forks_not_local'].append(repo_info)
        elif is_bot_related or is_cloudflare:
            if is_local or name in LOCAL_ACTIVE_PROJECTS:
                categories['keep_recommended'].append(repo_info)
            else:
                categories['bot_repos_not_local'].append(repo_info)
        elif not is_local:
            # GitHub only - check if it's worth keeping
            if stars > 0 or 'security' in desc or 'ai' in desc:
                categories['needs_review'].append(repo_info)
            else:
                categories['github_only_unused'].append(repo_info)
        else:
            categories['keep_recommended'].append(repo_info)
    
    return categories

def generate_delete_script(repos_to_delete: List[Dict]):
    """Generate a shell script to delete repos via GitHub CLI"""
    
    script_lines = [
        "#!/bin/bash",
        "# GitHub Repository Cleanup Script",
        f"# Generated: {datetime.now().isoformat()}",
        "#",
        "# This script will delete the following repositories:",
        "# Review carefully before running!",
        "",
        "# Prerequisites:",
        "# 1. Install GitHub CLI: https://cli.github.com/",
        "# 2. Authenticate: gh auth login",
        "# 3. Review the list below",
        "",
        "echo '=== Repositories to be deleted ==='",
    ]
    
    for repo in repos_to_delete:
        script_lines.append(f"echo '  - {repo['name']}'")
    
    script_lines.extend([
        "",
        "read -p 'Are you sure you want to delete these repos? (yes/no): ' confirm",
        "if [ \"\$confirm\" != \"yes\" ]; then",
        "    echo 'Aborting.'",
        "    exit 1",
        "fi",
        "",
        "# Delete repositories",
    ])
    
    for repo in repos_to_delete:
        script_lines.append(f"echo 'Deleting {repo['name']}...'")
        script_lines.append(f"gh repo delete yksanjo/{repo['name']} --yes || echo 'Failed to delete {repo['name']}'")
        script_lines.append("")
    
    script_lines.extend([
        "echo 'Cleanup complete!'",
        ""
    ])
    
    return '\n'.join(script_lines)

def main():
    print("=" * 80)
    print("GITHUB REPOSITORY CLEANUP ANALYSIS")
    print("=" * 80)
    print()
    
    categories = categorize_repos()
    
    # Print analysis
    print("📊 REPOSITORY CATEGORIES")
    print("-" * 80)
    
    print(f"\n🗑️  FORKS NOT LOCALLY ACTIVE ({len(categories['forks_not_local'])} repos):")
    for repo in categories['forks_not_local']:
        print(f"   ❌ {repo['name']:50} | Stars: {repo['stars']}")
    
    print(f"\n🤖 BOT/CLOUDFLARE REPOS NOT LOCAL ({len(categories['bot_repos_not_local'])} repos):")
    for repo in categories['bot_repos_not_local']:
        print(f"   ❌ {repo['name']:50} | Stars: {repo['stars']}")
    
    print(f"\n📦 GITHUB-ONLY UNUSED ({len(categories['github_only_unused'])} repos):")
    for repo in categories['github_only_unused'][:20]:  # Show first 20
        print(f"   ⚠️  {repo['name']:50} | Stars: {repo['stars']}")
    if len(categories['github_only_unused']) > 20:
        print(f"   ... and {len(categories['github_only_unused']) - 20} more")
    
    print(f"\n🔍 NEEDS REVIEW ({len(categories['needs_review'])} repos):")
    for repo in categories['needs_review']:
        print(f"   🤔 {repo['name']:50} | Stars: {repo['stars']}")
    
    print(f"\n✅ RECOMMENDED TO KEEP ({len(categories['keep_recommended'])} repos):")
    for repo in categories['keep_recommended'][:10]:  # Show first 10
        local_status = 'LOCAL' if repo['is_local'] else 'GITHUB-ONLY'
        fork_status = 'FORK' if repo['is_fork'] else ''
        print(f"   ✓ {repo['name']:50} | {local_status:10} | {fork_status} | Stars: {repo['stars']}")
    if len(categories['keep_recommended']) > 10:
        print(f"   ... and {len(categories['keep_recommended']) - 10} more")
    
    # Calculate totals
    high_confidence_delete = categories['forks_not_local'] + categories['bot_repos_not_local']
    potential_delete = categories['github_only_unused']
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"High confidence deletions (forks + unused bots): {len(high_confidence_delete)}")
    print(f"Potential deletions (unused GitHub-only):        {len(potential_delete)}")
    print(f"Repos to keep:                                   {len(categories['keep_recommended'])}")
    print(f"Repos needing manual review:                     {len(categories['needs_review'])}")
    print()
    
    # Generate cleanup scripts
    if high_confidence_delete:
        delete_script = generate_delete_script(high_confidence_delete)
        with open('delete_high_confidence.sh', 'w') as f:
            f.write(delete_script)
        os.chmod('delete_high_confidence.sh', 0o755)
        print("✅ Created: delete_high_confidence.sh")
        print(f"   This script will delete {len(high_confidence_delete)} repos (forks + unused bots)")
    
    if potential_delete:
        delete_script = generate_delete_script(potential_delete)
        with open('delete_potential.sh', 'w') as f:
            f.write(delete_script)
        os.chmod('delete_potential.sh', 0o755)
        print("✅ Created: delete_potential.sh")
        print(f"   This script will delete {len(potential_delete)} unused GitHub-only repos")
    
    # Save detailed report
    report = {
        'generated_at': datetime.now().isoformat(),
        'categories': categories,
        'summary': {
            'total_github_repos': len(GITHUB_REPOS),
            'total_local_repos': len(LOCAL_DIRS),
            'high_confidence_deletions': len(high_confidence_delete),
            'potential_deletions': len(potential_delete),
            'keep_recommended': len(categories['keep_recommended']),
            'needs_review': len(categories['needs_review'])
        }
    }
    
    with open('cleanup_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("✅ Created: cleanup_report.json")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review cleanup_report.json for full details")
    print("2. Run: ./delete_high_confidence.sh (for obvious deletions)")
    print("3. Review and optionally run: ./delete_potential.sh")
    print("4. Manually review repos in 'needs_review' category")
    print()
    print("⚠️  WARNING: Deletions are PERMANENT. Review carefully!")
    print("=" * 80)

if __name__ == "__main__":
    main()
