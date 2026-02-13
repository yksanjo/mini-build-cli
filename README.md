# GitHub Fork Mapper for Open Claw Project

## 🎯 Project Overview

This project maps all GitHub users who have forked from the [openclaw/openclaw](https://github.com/openclaw/openclaw) repository and analyzes their AI/agent-related activities. The goal is to identify and track the community of developers interested in AI agents through their Open Claw forks.

## 📊 Current Status

**Repository Stats (as of test):**
- **Repository**: openclaw/openclaw
- **Stars**: 171,410 ⭐
- **Forks**: 27,639 🍴
- **Description**: "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞"

**API Status**: ✅ Working
**Rate Limits**: 60 requests/hour (57 remaining)

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- `requests` library (install via `pip install requests`)

### Installation
```bash
# Clone or download the project files
# Install required packages
pip install requests
```

### Quick Start
1. **Test API access:**
   ```bash
   python test_github_scraper.py
   ```

2. **Run full scraping:**
   ```bash
   python github_fork_scraper.py
   ```

3. **Optional**: Enter a GitHub token when prompted for higher rate limits

## 📁 Project Structure

```
.
├── github_fork_scraper.py    # Main scraping and analysis script
├── test_github_scraper.py    # API test and verification script
├── README.md                 # This documentation
└── (Generated files during execution):
    ├── progress_*.json       # Progress saves
    ├── github_fork_analysis_*.json  # Full results (JSON)
    ├── github_fork_analysis_*.csv   # Full results (CSV)
    └── github_fork_summary_*.json   # Analysis summary
```

## 🔧 Features

### 1. **Fork Discovery**
- Fetches all forks from openclaw/openclaw repository
- Handles pagination automatically
- Respects GitHub rate limits

### 2. **User Analysis**
- Collects user profile information
- Analyzes for AI/agent keywords in:
  - User bio
  - User name
  - Repository names and descriptions
- Identifies agent-related developers

### 3. **Keyword Detection**
The system looks for these AI/agent-related keywords:
- `agent`, `ai`, `llm`, `gpt`, `claude`, `openai`, `anthropic`
- `autonomous`, `assistant`, `bot`, `automation`, `workflow`
- `orchestration`, `multi-agent`, `swarm`, `crew`, `autogen`
- `langchain`, `llamaindex`, `haystack`, `semantic-kernel`
- `claw`, `openclaw`, `agentic`, `reasoning`, `cognitive`

### 4. **Data Export**
- **JSON**: Full structured data
- **CSV**: Tabular data for spreadsheets
- **Progress saves**: Automatic checkpointing
- **Summary reports**: Key metrics and insights

## 📈 Expected Output

The scraper will generate:
1. **User Profiles**: Login, name, company, location, bio, etc.
2. **Fork Information**: When they forked, fork URL
3. **Agent Analysis**: Whether user is agent-related, keywords found
4. **Statistics**: Total users, agent percentage, top keywords
5. **Sample Data**: First 10 agent users with details

## ⚡ Performance Notes

### Rate Limits
- **Without token**: 60 requests/hour (1 request/second recommended)
- **With token**: 5,000 requests/hour

### Estimated Time
- **27,639 forks** to analyze
- **~1 request/second** = ~7.7 hours without token
- **Progress saves** every 5 users
- **Resume capability** from progress files

## 🔐 GitHub Token (Optional but Recommended)

Get a token from: https://github.com/settings/tokens

**Permissions needed:**
- `public_repo` (read-only)
- Or no special permissions for public data

**Benefits:**
- Higher rate limits (5,000 vs 60 requests/hour)
- More reliable access
- Faster scraping

## 🎮 Usage Examples

### Basic Usage
```bash
python github_fork_scraper.py
```

### With GitHub Token
```bash
# The script will prompt for token, or you can modify the code
```

### Monitor Progress
```bash
# Check generated files
ls -la progress_*.json
ls -la github_fork_analysis_*.json
```

### Resume from Progress
```python
# The script automatically saves progress
# If interrupted, you can modify the script to load from progress files
```

## 📊 Analysis Goals

1. **Community Mapping**: Who are the Open Claw forkers?
2. **Agent Ecosystem**: What percentage are AI/agent developers?
3. **Trend Analysis**: When did people fork? (temporal patterns)
4. **Network Effects**: Can we identify clusters or communities?
5. **Outreach Targets**: Identify potential collaborators or users

## 🛠️ Technical Details

### API Endpoints Used
- `GET /repos/openclaw/openclaw` - Repository info
- `GET /repos/openclaw/openclaw/forks` - Fork list
- `GET /users/{username}` - User details
- `GET /users/{username}/repos` - User repositories
- `GET /rate_limit` - Rate limit status

### Error Handling
- Rate limit detection and automatic waiting
- Connection retries
- Invalid user handling
- Progress saving on errors

### Data Privacy
- Only collects public GitHub data
- No authentication required for basic usage
- Respects GitHub's Terms of Service

## 🔮 Future Enhancements

### Planned Features
1. **Social Network Analysis**: Map connections between forkers
2. **Activity Tracking**: Monitor recent commits and activity
3. **Repository Analysis**: Deep dive into forked repositories
4. **Trend Visualization**: Charts and graphs of findings
5. **Real-time Updates**: Periodic re-scraping for new forks

### Integration Possibilities
1. **OpenCLaw Integration**: Direct integration with OpenCLaw system
2. **Database Backend**: Store results in SQLite/PostgreSQL
3. **Web Dashboard**: Real-time monitoring interface
4. **API Service**: REST API for querying results
5. **Alert System**: Notifications for new agent-related forks

## 🤝 Contributing

This is an open project for mapping the Open Claw community. Contributions welcome!

### Areas for Contribution
- Performance optimization
- Additional analysis features
- Visualization tools
- Documentation improvements
- Error handling enhancements

## 📄 License

MIT License - See included LICENSE file (if any)

## ⚠️ Disclaimer

This tool:
- Only accesses public GitHub data
- Respects rate limits and Terms of Service
- Is for research and community analysis purposes
- Should not be used for spam or harassment

## 📞 Support

For issues or questions:
1. Check the GitHub API status: https://www.githubstatus.com/
2. Review rate limit documentation
3. Test with the verification script first

---

**Happy Fork Mapping!** 🦞🔍

*"Tracking the lobster way through GitHub forks"*