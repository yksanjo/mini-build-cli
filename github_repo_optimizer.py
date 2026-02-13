#!/usr/bin/env python3
"""
GitHub Repository Optimizer
Analyzes repositories and suggests improvements for a professional profile
WITHOUT deleting anything - only suggesting archives, better descriptions, etc.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class RepoRecommendation:
    """Repository optimization recommendation"""
    repo_name: str
    priority: str  # high, medium, low
    category: str
    current_state: str
    recommendation: str
    action: str
    example: Optional[str] = None


class GitHubRepoOptimizer:
    """Optimizer for GitHub repository presentation"""
    
    # Quality thresholds
    STALE_DAYS = 365  # Consider archiving after 1 year
    NO_DESC_PENALTY = 10
    SHORT_DESC_THRESHOLD = 30
    
    def __init__(self, data_file: str = "portfolio_summary.json"):
        self.data_file = data_file
        self.data = self._load_data()
        self.recommendations: List[RepoRecommendation] = []
        self.repos_data: List[Dict] = []
    
    def _load_data(self) -> Dict:
        """Load portfolio data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Try alternative files
        alt_files = ["github_repos_categorized.json", "github_repos_inventory.json"]
        for file in alt_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    repos = json.load(f)
                    return {"showcase_recommendations": repos, "username": "yksanjo"}
        
        return {}
    
    def analyze_all_repos(self) -> List[RepoRecommendation]:
        """Analyze all repositories and generate recommendations"""
        
        # Load full repo list
        repos = self.data.get('showcase_recommendations', [])
        
        # Try to load more complete data
        for file in ["github_repos_categorized.json", "github_repos_inventory.json"]:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    self.repos_data = json.load(f)
                break
        
        if not self.repos_data:
            self.repos_data = repos
        
        print(f"📊 Analyzing {len(self.repos_data)} repositories...\n")
        
        # Run all analysis checks
        self._check_descriptions()
        self._check_stale_repos()
        self._check_missing_topics()
        self._check_homepage_urls()
        self._check_readme_quality()
        self._check_license_presence()
        self._check_fork_clarity()
        self._check_naming_conventions()
        self._check_category_consistency()
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        self.recommendations.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return self.recommendations
    
    def _check_descriptions(self):
        """Check for missing or poor descriptions"""
        for repo in self.repos_data:
            name = repo.get('name', '')
            desc = repo.get('description', '') or ''
            
            if not desc:
                # Generate a suggestion based on repo name and content
                suggestion = self._generate_description_suggestion(repo)
                
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="high",
                    category="Description",
                    current_state="No description",
                    recommendation="Add a professional description",
                    action=f"Edit repo → Add description: '{suggestion}'",
                    example=suggestion
                ))
            elif len(desc) < self.SHORT_DESC_THRESHOLD:
                improved = self._improve_description(desc, repo)
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="medium",
                    category="Description",
                    current_state=f"Short description: '{desc}'",
                    recommendation="Expand description for clarity",
                    action=f"Update to: '{improved}'",
                    example=improved
                ))
    
    def _check_stale_repos(self):
        """Identify potentially stale repositories"""
        for repo in self.repos_data:
            days = repo.get('days_since_update', 0)
            name = repo.get('name', '')
            is_archived = repo.get('is_archived', False)
            is_fork = repo.get('is_fork', False)
            
            if days > self.STALE_DAYS and not is_archived and not is_fork:
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="medium",
                    category="Maintenance",
                    current_state=f"No updates for {days} days",
                    recommendation="Consider archiving to keep profile clean",
                    action="Settings → Archive repository (reversible!)",
                    example=f"Archive: Last updated {days} days ago"
                ))
    
    def _check_missing_topics(self):
        """Check for missing topic tags"""
        for repo in self.repos_data:
            topics = repo.get('topics', [])
            name = repo.get('name', '')
            lang = repo.get('primary_language', '')
            category = repo.get('category', '')
            
            if not topics or len(topics) < 3:
                suggested_topics = self._suggest_topics(name, lang, category)
                
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="medium",
                    category="Topics/Tags",
                    current_state=f"{len(topics)} topics: {', '.join(topics[:3]) if topics else 'None'}",
                    recommendation="Add 3-5 relevant topic tags",
                    action=f"Edit → Add topics: {', '.join(suggested_topics)}",
                    example=', '.join(suggested_topics)
                ))
    
    def _check_homepage_urls(self):
        """Check for missing demo/homepage URLs"""
        for repo in self.repos_data:
            name = repo.get('name', '')
            homepage = repo.get('homepage', '')
            desc = repo.get('description', '') or ''
            
            # Check if it might be a web project
            is_web_project = any(word in name.lower() or word in desc.lower() 
                               for word in ['web', 'app', 'site', 'ui', 'dashboard', 'client'])
            
            if is_web_project and not homepage:
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="low",
                    category="Homepage",
                    current_state="No homepage URL",
                    recommendation="Add demo or documentation URL",
                    action="Edit → Add website URL",
                    example=f"https://{name.lower().replace('_', '-')}.vercel.app"
                ))
    
    def _check_readme_quality(self):
        """Check README presence (we can't check content, just existence)"""
        for repo in self.repos_data:
            name = repo.get('name', '')
            has_readme = repo.get('has_readme')
            
            # We don't have this data from the API, so we'll recommend checking
            # This is a reminder recommendation
            if repo.get('showcase_score', 0) > 40:  # High-value repos
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="medium",
                    category="README",
                    current_state="README status unknown",
                    recommendation="Ensure README has: features, install instructions, screenshots",
                    action="Check README.md and enhance if needed",
                    example="See README template generator"
                ))
    
    def _check_license_presence(self):
        """Check for missing licenses"""
        for repo in self.repos_data:
            name = repo.get('name', '')
            license_name = repo.get('license', 'None')
            
            if license_name == 'None' and not repo.get('is_fork', False):
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="low",
                    category="License",
                    current_state="No license file",
                    recommendation="Add an open-source license",
                    action="Add file → Create LICENSE → Choose MIT/Apache",
                    example="MIT License"
                ))
    
    def _check_fork_clarity(self):
        """Ensure forks are clearly understood"""
        forks = [r for r in self.repos_data if r.get('is_fork', False)]
        
        if len(forks) > 10:  # If many forks, suggest organizing
            self.recommendations.append(RepoRecommendation(
                repo_name="Multiple forks",
                priority="low",
                category="Organization",
                current_state=f"{len(forks)} forked repositories",
                recommendation="Consider starring instead of forking for reference",
                action="Review forks → Archive unused ones (keep active contributions)",
                example=None
            ))
    
    def _check_naming_conventions(self):
        """Check repository naming"""
        for repo in self.repos_data:
            name = repo.get('name', '')
            
            # Check for inconsistent naming
            issues = []
            if ' ' in name:
                issues.append("Contains spaces")
            if name != name.lower() and '-' in name:
                issues.append("Mixed case with hyphens")
            
            if issues and not repo.get('is_fork', False):
                self.recommendations.append(RepoRecommendation(
                    repo_name=name,
                    priority="low",
                    category="Naming",
                    current_state=f"Naming: {', '.join(issues)}",
                    recommendation="Use kebab-case (my-project-name) for consistency",
                    action="⚠️ Cannot rename without breaking links - consider for new repos",
                    example="my-awesome-project"
                ))
    
    def _check_category_consistency(self):
        """Suggest organization by category"""
        categories = Counter([r.get('category', 'Uncategorized') for r in self.repos_data])
        
        # Suggest creating lists or topics by category
        for category, count in categories.most_common(5):
            if count > 5 and category != 'Uncategorized':
                self.recommendations.append(RepoRecommendation(
                    repo_name=f"{category} repos",
                    priority="low",
                    category="Organization",
                    current_state=f"{count} repositories in {category}",
                    recommendation=f"Consider creating a GitHub List for {category} projects",
                    action=f"Profile → Lists → Create '{category} Projects' list",
                    example=None
                ))
    
    def _generate_description_suggestion(self, repo: Dict) -> str:
        """Generate a professional description based on repo content"""
        name = repo.get('name', '')
        category = repo.get('category', '')
        lang = repo.get('primary_language', 'code')
        
        # Clean up name
        clean_name = name.replace('-', ' ').replace('_', ' ').title()
        
        templates = {
            'AI/ML': f"{clean_name} - AI-powered tool built with {lang}",
            'Web Frontend': f"{clean_name} - Modern web application using {lang}",
            'Web Backend': f"{clean_name} - Backend API and services in {lang}",
            'Security': f"{clean_name} - Security tool for protecting systems",
            'DevOps/Infra': f"{clean_name} - Infrastructure automation with {lang}",
            'CLI/Tools': f"{clean_name} - Command-line utility built in {lang}",
            'Mobile': f"{clean_name} - Mobile app development project",
            'Data/Database': f"{clean_name} - Data processing and management tool",
            'Game Dev': f"{clean_name} - Game development project in {lang}",
            'Blockchain': f"{clean_name} - Blockchain and Web3 application",
        }
        
        return templates.get(category, f"{clean_name} - Built with {lang}")
    
    def _improve_description(self, current: str, repo: Dict) -> str:
        """Improve an existing short description"""
        category = repo.get('category', '')
        lang = repo.get('primary_language', '')
        
        # Expand common abbreviations
        improved = current
        if not improved.endswith('.'):
            improved += '.'
        
        # Add context if missing
        if category and category not in improved:
            improved += f" Built with {lang}."
        
        return improved
    
    def _suggest_topics(self, name: str, lang: str, category: str) -> List[str]:
        """Suggest topic tags based on repository content"""
        topics = []
        
        # Add language
        if lang:
            topics.append(lang.lower())
        
        # Add category-based topics
        category_topics = {
            'AI/ML': ['machine-learning', 'ai', 'automation'],
            'Web Frontend': ['frontend', 'web', 'ui'],
            'Web Backend': ['backend', 'api', 'server'],
            'Security': ['security', 'cybersecurity', 'tools'],
            'DevOps/Infra': ['devops', 'infrastructure', 'automation'],
            'CLI/Tools': ['cli', 'command-line', 'tools'],
            'Mobile': ['mobile', 'app'],
            'Data/Database': ['data', 'database'],
            'Game Dev': ['game', 'gaming'],
            'Blockchain': ['blockchain', 'web3'],
        }
        
        topics.extend(category_topics.get(category, ['project']))
        
        # Add name-based inference
        name_lower = name.lower()
        if 'bot' in name_lower:
            topics.append('bot')
        if 'scraper' in name_lower:
            topics.append('scraper')
        if 'ai' in name_lower:
            topics.append('artificial-intelligence')
        if 'mcp' in name_lower:
            topics.append('mcp')
        
        return list(set(topics))[:5]  # Max 5 topics
    
    def generate_optimization_report(self) -> str:
        """Generate a comprehensive optimization report"""
        
        if not self.recommendations:
            return "No optimization recommendations found."
        
        # Group by priority
        high = [r for r in self.recommendations if r.priority == 'high']
        medium = [r for r in self.recommendations if r.priority == 'medium']
        low = [r for r in self.recommendations if r.priority == 'low']
        
        report = f"""# 🔧 GitHub Repository Optimization Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Repositories Analyzed: {len(self.repos_data)}

## 📊 Summary

| Priority | Count | Action |
|----------|-------|--------|
| 🔴 High | {len(high)} | Fix immediately |
| 🟡 Medium | {len(medium)} | Fix this week |
| 🟢 Low | {len(low)} | Fix when convenient |

---

## 🔴 High Priority ({len(high)} items)

"""
        
        for rec in high:
            report += self._format_recommendation(rec)
        
        report += f"\n## 🟡 Medium Priority ({len(medium)} items)\n\n"
        for rec in medium:
            report += self._format_recommendation(rec)
        
        report += f"\n## 🟢 Low Priority ({len(low)} items)\n\n"
        for rec in low:
            report += self._format_recommendation(rec)
        
        # Add category summary
        report += "\n## 📁 Recommendations by Category\n\n"
        categories = Counter([r.category for r in self.recommendations])
        for cat, count in categories.most_common():
            report += f"- **{cat}**: {count} recommendations\n"
        
        # Add quick wins section
        report += """
## ⚡ Quick Wins (Do These First)

1. **Add descriptions** to repos with "No description" - highest impact
2. **Archive stale repos** older than 1 year with no updates
3. **Add topic tags** to your top 10 showcase repositories
4. **Pin your best 6 repos** on your profile

---

*This report suggests improvements only. Nothing will be deleted or changed automatically.*
"""
        
        return report
    
    def _format_recommendation(self, rec: RepoRecommendation) -> str:
        """Format a single recommendation for the report"""
        text = f"""### {rec.repo_name}

**Issue**: {rec.current_state}

**Recommendation**: {rec.recommendation}

**Action**: {rec.action}
"""
        if rec.example:
            text += f"\n**Example**: `{rec.example}`\n"
        
        text += "\n---\n\n"
        return text
    
    def export_recommendations(self, filename: str = "repo_optimization_report.md"):
        """Export recommendations to file"""
        report = self.generate_optimization_report()
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Optimization report exported to {filename}")
        return filename
    
    def generate_action_checklist(self) -> str:
        """Generate a simple action checklist"""
        high_priority = [r for r in self.recommendations if r.priority == 'high']
        
        checklist = """# ✅ GitHub Optimization Checklist

## This Week's Tasks

"""
        
        # Group by action type
        desc_tasks = [r for r in high_priority if r.category == 'Description']
        archive_tasks = [r for r in self.recommendations if r.category == 'Maintenance']
        topic_tasks = [r for r in self.recommendations if r.category == 'Topics/Tags'][:10]
        
        checklist += f"""### 📝 Fix Descriptions ({len(desc_tasks)} repos)

"""
        for rec in desc_tasks[:10]:  # Top 10
            checklist += f"- [ ] **{rec.repo_name}**: Add description\n"
            if rec.example:
                checklist += f"  - Suggestion: `{rec.example}`\n"
        
        checklist += f"""

### 📦 Archive Stale Repos ({len(archive_tasks)} repos)

"""
        for rec in archive_tasks[:10]:
            checklist += f"- [ ] **{rec.repo_name}**: {rec.current_state}\n"
        
        checklist += f"""

### 🏷️ Add Topic Tags ({len(topic_tasks)} repos)

"""
        for rec in topic_tasks:
            checklist += f"- [ ] **{rec.repo_name}**: Add topics `{rec.example}`\n"
        
        checklist += """

## Profile-Level Tasks

- [ ] Pin top 6 repositories to profile
- [ ] Create profile README (see GENERATED_PROFILE_README.md)
- [ ] Review and organize with GitHub Lists

---

*Keep this checklist updated as you complete tasks*
"""
        
        return checklist


def main():
    print("=" * 70)
    print("🔧 GITHUB REPOSITORY OPTIMIZER")
    print("=" * 70)
    
    optimizer = GitHubRepoOptimizer()
    
    # Run analysis
    recommendations = optimizer.analyze_all_repos()
    
    # Print summary
    print(f"\n📋 Found {len(recommendations)} optimization opportunities\n")
    
    high = len([r for r in recommendations if r.priority == 'high'])
    medium = len([r for r in recommendations if r.priority == 'medium'])
    low = len([r for r in recommendations if r.priority == 'low'])
    
    print(f"   🔴 High Priority: {high}")
    print(f"   🟡 Medium Priority: {medium}")
    print(f"   🟢 Low Priority: {low}")
    
    # Export report
    print("\n📄 Generating reports...")
    optimizer.export_recommendations("repo_optimization_report.md")
    
    # Generate checklist
    checklist = optimizer.generate_action_checklist()
    with open("optimization_checklist.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    print("✅ Checklist saved to optimization_checklist.md")
    
    # Print top recommendations
    print("\n" + "=" * 70)
    print("🔴 TOP 5 HIGH PRIORITY FIXES")
    print("=" * 70)
    
    high_priority = [r for r in recommendations if r.priority == 'high'][:5]
    for i, rec in enumerate(high_priority, 1):
        print(f"\n{i}. {rec.repo_name}")
        print(f"   Issue: {rec.current_state}")
        print(f"   Fix: {rec.recommendation}")
        if rec.example:
            print(f"   Suggested: {rec.example}")
    
    print("\n" + "=" * 70)
    print("✨ Next Steps")
    print("=" * 70)
    print("\n1. Open repo_optimization_report.md for full details")
    print("2. Use optimization_checklist.md to track progress")
    print("3. Start with high-priority description fixes")
    print("4. Archive (don't delete!) stale repositories")
    print("\n💡 Remember: Archiving is reversible and keeps your work!")


if __name__ == "__main__":
    main()
