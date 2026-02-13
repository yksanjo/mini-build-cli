#!/usr/bin/env python3
"""
Interactive GitHub Cleanup Tool
Deletes forks and bot repos that aren't your active OpenClaw projects
"""

import subprocess
import json

# Load the report
with open('cleanup_report.json', 'r') as f:
    report = json.load(f)

def delete_repo(repo_name):
    """Delete a repository using GitHub CLI"""
    cmd = ['gh', 'repo', 'delete', f'yksanjo/{repo_name}', '--yes']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  ✅ Deleted: {repo_name}")
            return True
        else:
            print(f"  ❌ Failed: {repo_name} - {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {repo_name} - {e}")
        return False

def main():
    print("=" * 80)
    print("GITHUB CLEANUP - INTERACTIVE MODE")
    print("=" * 80)
    print()
    
    # Get high confidence deletions
    forks = report['categories']['forks_not_local']
    bots = report['categories']['bot_repos_not_local']
    
    print(f"🗑️  FORKS TO DELETE ({len(forks)} repos):")
    for repo in forks:
        print(f"   - {repo['name']}")
    
    print(f"\n🤖 BOT REPOS TO DELETE ({len(bots)} repos):")
    for repo in bots:
        print(f"   - {repo['name']}")
    
    print()
    print("=" * 80)
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will PERMANENTLY delete these repositories!")
    print("   Your ACTIVE OpenClaw projects (clawd, clawdbot-deepseek, etc.) are LOCAL ONLY")
    print("   and will NOT be affected by this cleanup.\n")
    
    response = input("Delete FORKS? (yes/no): ").strip().lower()
    if response == 'yes':
        print("\nDeleting forks...")
        deleted = 0
        for repo in forks:
            if delete_repo(repo['name']):
                deleted += 1
        print(f"\nDeleted {deleted}/{len(forks)} forks")
    else:
        print("Skipped fork deletion")
    
    print()
    response = input("Delete BOT repos? (yes/no): ").strip().lower()
    if response == 'yes':
        print("\nDeleting bot repos...")
        deleted = 0
        for repo in bots:
            if delete_repo(repo['name']):
                deleted += 1
        print(f"\nDeleted {deleted}/{len(bots)} bot repos")
    else:
        print("Skipped bot deletion")
    
    # Optional: Clean up unused GitHub-only repos
    print()
    unused = report['categories']['github_only_unused']
    print(f"\n📦 UNUSED GITHUB-ONLY REPOS ({len(unused)} repos)")
    print("   These repos exist only on GitHub (not locally)")
    response = input("Show and optionally delete these? (yes/no): ").strip().lower()
    
    if response == 'yes':
        for repo in unused:
            r = input(f"   Delete '{repo['name']}'? (y/n/q): ").strip().lower()
            if r == 'q':
                break
            elif r == 'y':
                delete_repo(repo['name'])
    
    print()
    print("=" * 80)
    print("CLEANUP COMPLETE!")
    print("=" * 80)
    print("\nYour GitHub is now cleaner! 🎉")
    print("Remember: Your active OpenClaw projects are still local-only and safe.")

if __name__ == "__main__":
    main()
