# Final GitHub Cleanup Instructions

## Step 1: Grant Delete Permission

Run this command to add delete permission to GitHub CLI:

```bash
gh auth login --scopes repo,delete_repo
```

Or refresh existing auth:

```bash
gh auth refresh -h github.com -s delete_repo
```

## Step 2: Run the Cleanup Script

After authenticating, run:

```bash
cd /Users/yoshikondo && ./do_cleanup.sh
```

## What Will Be Deleted

### Forks (9 repos):
- camera-heart-rate-monitor-web
- camera-heart-rate-monitor
- whisper-plus
- all-in-rag
- Dirt-Samples
- cs249r_book
- TrendRadar
- tinytag
- yt-dlp

### Bot Repos (11 repos):
- ai-agent-waf
- agent-hr
- agent-finance
- invoice-reminder-bot
- identityvault-agents
- InvoiceBot
- Pixel-Perfect-Agent
- chatbot
- tiny-chatbot
- pr-health-bot
- rap-beat-callbot

## Alternative: Manual Deletion via Web

If CLI doesn't work, you can bulk delete via GitHub web:

1. Go to: https://github.com/yksanjo?tab=repositories
2. Click into each repo above
3. Settings → Danger Zone → Delete

## Your Active Projects (Safe)

These remain LOCAL ONLY and won't be affected:
- clawd
- clawdbot-deepseek
- clawdbot-launchpad
- openclawsandbox
- moltworker
- moltworker-cloudflare
- moltworker-simplified

---

Run the cleanup after authenticating with delete_repo scope!
