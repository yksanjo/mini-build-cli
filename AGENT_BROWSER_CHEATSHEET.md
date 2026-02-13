# Agent Browser Cheat Sheet

## 🚀 Installation
```bash
npm install -g agent-browser      # Install globally
agent-browser install             # Download Chromium
npx agent-browser --help          # Use without installation
```

## 📋 Essential Commands

### Navigation
```bash
agent-browser open <url>          # Open URL (aliases: goto, navigate)
agent-browser close               # Close browser (aliases: quit, exit)
agent-browser get url             # Get current URL
agent-browser get title           # Get page title
```

### Element Interaction
```bash
agent-browser click <selector>    # Click element
agent-browser fill <sel> <text>   # Clear and fill field
agent-browser type <sel> <text>   # Type into field
agent-browser press <key>         # Press key (Enter, Tab, etc.)
agent-browser hover <selector>    # Hover over element
```

### Form Elements
```bash
agent-browser select <sel> <val>  # Select dropdown option
agent-browser check <selector>    # Check checkbox
agent-browser uncheck <selector>  # Uncheck checkbox
agent-browser upload <sel> <file> # Upload file
```

### Getting Information
```bash
agent-browser get text <selector> # Get text content
agent-browser get html <selector> # Get innerHTML
agent-browser get value <selector> # Get input value
agent-browser get attr <sel> <attr> # Get attribute
agent-browser get count <selector> # Count elements
agent-browser snapshot            # Get AI-friendly element refs
```

### Screenshots & PDF
```bash
agent-browser screenshot [file]   # Take screenshot
agent-browser screenshot --full   # Full page screenshot
agent-browser pdf <file>          # Save as PDF
```

### Scrolling
```bash
agent-browser scroll down 500     # Scroll down 500px
agent-browser scroll up 300       # Scroll up 300px
agent-browser scrollintoview <sel> # Scroll element into view
```

## 🎯 Common Selectors

### By Reference (from snapshot)
```bash
agent-browser click @e1           # Click element reference @e1
agent-browser fill @e2 "text"     # Fill element reference @e2
```

### CSS Selectors
```bash
agent-browser click "#submit"     # By ID
agent-browser fill ".email" "text" # By class
agent-browser click "button"      # By tag name
agent-browser click "[type=submit]" # By attribute
```

### Role-based (Accessibility)
```bash
agent-browser find role button click --name "Submit"
agent-browser find role link click --name "Learn More"
```

## ⚙️ Useful Options
```bash
--headless                        # Run without UI
--viewport 1920x1080              # Set window size
--delay 1000                      # 1s delay between actions
--timeout 30000                   # 30s timeout
--cdp 9222                        # Connect to existing browser
--wait-for "#element"             # Wait for element
```

## 🔄 Command Chaining
```bash
# Chain commands with &&
agent-browser open https://google.com \
  && agent-browser fill "textarea" "search query" \
  && agent-browser press Enter \
  && agent-browser screenshot results.png \
  && agent-browser close
```

## 📝 Example Scripts

### Quick Test Script
```bash
#!/bin/bash
agent-browser --headless open https://httpbin.org/html
agent-browser get title
agent-browser get url
agent-browser screenshot test.png
agent-browser close
```

### Form Automation
```bash
#!/bin/bash
agent-browser --headless open https://example.com/form
agent-browser fill "#name" "John Doe"
agent-browser fill "#email" "john@example.com"
agent-browser select "#country" "US"
agent-browser check "#terms"
agent-browser click "#submit"
agent-browser screenshot confirmation.png
agent-browser close
```

### Page Scraper
```bash
#!/bin/bash
agent-browser --headless open https://example.com
echo "Title: $(agent-browser get title)"
echo "H1: $(agent-browser get text 'h1')"
echo "Links: $(agent-browser get count 'a')"
echo "Paragraphs: $(agent-browser get count 'p')"
agent-browser close
```

## 🤖 AI Agent Workflow

### Recommended AI Workflow
```bash
# 1. Navigate to page
agent-browser open https://example.com

# 2. Get interactive elements
agent-browser snapshot
# Output: @e1: button "Submit", @e2: input "Email", etc.

# 3. Interact using refs
agent-browser fill @e2 "test@example.com"
agent-browser click @e1

# 4. Take screenshot
agent-browser screenshot result.png

# 5. Close
agent-browser close
```

## 🐛 Troubleshooting

### Quick Fixes
```bash
# Browser not installed
agent-browser install

# Linux dependencies
agent-browser install --with-deps

# Command not found
npx agent-browser --help

# Element not found
agent-browser snapshot  # Check available elements
```

### Debug Commands
```bash
# Show all commands
agent-browser --help

# Command-specific help
agent-browser open --help
agent-browser click --help
agent-browser get --help

# Version info
agent-browser --version
```

## 🎪 Fun Examples

### Batch Screenshots
```bash
for site in google.com github.com news.ycombinator.com; do
  agent-browser --headless open https://$site
  agent-browser screenshot ${site}.png
  agent-browser close
done
```

### Interactive Demo
```bash
# Open browser (visible)
agent-browser open https://google.com
# In another terminal:
agent-browser snapshot
agent-browser screenshot interactive.png
agent-browser close
```

## 📚 Help & Resources
```bash
agent-browser --help                    # All commands
agent-browser <command> --help          # Command help
```

**GitHub**: https://github.com/vercel-labs/agent-browser  
**Examples**: https://github.com/vercel-labs/agent-browser/tree/main/examples

---

## 💡 Pro Tips

1. **Start with `snapshot`** for AI agents - it gives element references
2. **Use `--headless`** for automation scripts
3. **Chain with `&&`** for simple workflows
4. **Check help often** - new features added regularly
5. **Combine with shell scripts** for complex automation

---

**Print this cheatsheet:** `cat AGENT_BROWSER_CHEATSHEET.md`  
**Quick start:** `./agent_browser_boot.sh`  
**Test commands:** `./test_agent_browser_commands.sh`

Happy automating! 🚀