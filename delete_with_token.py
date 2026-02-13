#!/usr/bin/env python3
"""
Delete GitHub repos using a Personal Access Token with delete_repo scope
Usage: python3 delete_with_token.py <github_token>
"""

import sys
import requests
import json

# Repos to delete (from analysis)
FORKS = [
    "camera-heart-rate-monitor-web", "camera-heart-rate-monitor", "whisper-plus",
    "all-in-rag", "Dirt-Samples", "cs249r_book", "TrendRadar", "tinytag", "yt-dlp"
]

BOTS = [
    "ai-agent-waf", "agent-hr", "agent-finance", "invoice-reminder-bot",
    "identityvault-agents", "InvoiceBot", "Pixel-Perfect-Agent", "chatbot",
    "tiny-chatbot", "pr-health-bot", "rap-beat-callbot"
]

UNUSED = [
    "attack-surface-ai", "ai-security-suite", "You-Dont-Need-jQuery",
    "identity-studio", "social-media-scheduler", "saas-churn-predictor",
    "github-star-notifier", "dead-link-checker", "competitor-price-tracker",
    "code-review-time-tracker", "api-rate-limit-monitor", "quick-scaffold",
    "mock-api-gen", "git-hook-setup", "task-run", "diff-focus-vscode",
    "RateGuard", "ReviewClock", "ChurnGuard", "StarAlert-", "PriceWatch",
    "SocialQueue", "LinkCheck", "roadmap-dashboard", "feature-flag-auditor",
    "pr-summarizer", "repo-recommendations", "research-project-manager-ios",
    "Yoshi-s_Transcriber", "neon-dodger", "xy-shader-cookbook",
    "strudel-music-lab", "audio2strudel", "3D-Solar-System-Explorer",
    "roblox-world-generator", "cloud-finops", "ml-systems-visualizations",
    "basketball-3d-game", "clipboard-copilot", "repoboard",
    "ml-experiment-toolkit", "milky-way-visualization", "pydub-plus",
    "mystery-circle", "ModelAudit", "Cursor-creature1", "supplyhield",
    "Drum2Strudel"
]

def delete_repo(repo_name, token):
    """Delete a repository via GitHub API"""
    url = f"https://api.github.com/repos/yksanjo/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return True, "Deleted"
    elif response.status_code == 404:
        return False, "Not found (already deleted?)"
    elif response.status_code == 403:
        return False, "Forbidden - token lacks delete_repo permission"
    else:
        return False, f"HTTP {response.status_code}: {response.text[:100]}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 delete_with_token.py <github_token>")
        print("")
        print("Get a token with 'delete_repo' scope from:")
        print("https://github.com/settings/tokens/new")
        print("")
        print("Scopes needed: delete_repo, repo")
        sys.exit(1)
    
    token = sys.argv[1]
    
    # Verify token
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Invalid token: {response.status_code}")
        sys.exit(1)
    
    user = response.json()
    print(f"✅ Authenticated as: {user['login']}")
    print("")
    
    # Show what will be deleted
    total = len(FORKS) + len(BOTS) + len(UNUSED)
    print(f"Ready to delete {total} repositories:")
    print(f"  - {len(FORKS)} forks")
    print(f"  - {len(BOTS)} bot repos")
    print(f"  - {len(UNUSED)} unused GitHub-only repos")
    print("")
    
    confirm = input("Type 'DELETE ALL' to proceed: ")
    if confirm != "DELETE ALL":
        print("Aborted.")
        sys.exit(0)
    
    # Delete forks
    print("\n🗑️  Deleting forks...")
    for repo in FORKS:
        success, msg = delete_repo(repo, token)
        status = "✅" if success else "❌"
        print(f"  {status} {repo}: {msg}")
    
    # Delete bots
    print("\n🤖 Deleting bot repos...")
    for repo in BOTS:
        success, msg = delete_repo(repo, token)
        status = "✅" if success else "❌"
        print(f"  {status} {repo}: {msg}")
    
    # Delete unused
    print("\n📦 Deleting unused repos...")
    deleted = 0
    failed = 0
    for repo in UNUSED:
        success, msg = delete_repo(repo, token)
        status = "✅" if success else "❌"
        print(f"  {status} {repo}: {msg}")
        if success:
            deleted += 1
        else:
            failed += 1
    
    print(f"\n📊 Summary: {deleted} deleted, {failed} failed")
    print("\n✅ Cleanup complete!")
    print("\nRemaining repos with 1+ stars that may need manual review:")
    print("  - Check cleanup_report.json for full list")

if __name__ == "__main__":
    main()
