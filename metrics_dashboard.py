#!/usr/bin/env python3
"""
Metrics Dashboard for tracking promotion progress
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List

class MetricsDashboard:
    def __init__(self):
        self.metrics_file = "promotion_metrics.json"
        self.load_metrics()
        
    def load_metrics(self):
        """Load existing metrics or create new"""
        try:
            with open(self.metrics_file, 'r') as f:
                self.metrics = json.load(f)
        except FileNotFoundError:
            self.metrics = {
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "github": {
                    "stars": 0,
                    "forks": 0,
                    "issues": 0,
                    "daily_stars": [],
                    "daily_forks": []
                },
                "website": {
                    "visitors": 0,
                    "signups": 0,
                    "conversion_rate": 0.0,
                    "daily_visitors": []
                },
                "social": {
                    "twitter_followers": 0,
                    "linkedin_connections": 0,
                    "discord_members": 0,
                    "newsletter_subscribers": 0
                },
                "community": {
                    "active_users": 0,
                    "contributors": 0,
                    "feedback_count": 0,
                    "partnerships": 0
                },
                "revenue": {
                    "total_earnings": 0.0,
                    "active_paying_users": 0,
                    "mrr": 0.0
                }
            }
            self.save_metrics()
    
    def save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def update_github_metrics(self, stars: int = None, forks: int = None, issues: int = None):
        """Update GitHub metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if stars is not None:
            self.metrics["github"]["stars"] = stars
            self.metrics["github"]["daily_stars"].append({
                "date": today,
                "count": stars
            })
        
        if forks is not None:
            self.metrics["github"]["forks"] = forks
            self.metrics["github"]["daily_forks"].append({
                "date": today,
                "count": forks
            })
        
        if issues is not None:
            self.metrics["github"]["issues"] = issues
        
        self.save_metrics()
    
    def update_website_metrics(self, visitors: int = None, signups: int = None):
        """Update website metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if visitors is not None:
            self.metrics["website"]["visitors"] = visitors
            self.metrics["website"]["daily_visitors"].append({
                "date": today,
                "count": visitors
            })
        
        if signups is not None:
            self.metrics["website"]["signups"] = signups
        
        # Calculate conversion rate
        if visitors and signups:
            self.metrics["website"]["conversion_rate"] = round((signups / visitors) * 100, 2)
        
        self.save_metrics()
    
    def update_social_metrics(self, platform: str, count: int):
        """Update social media metrics"""
        if platform == "twitter":
            self.metrics["social"]["twitter_followers"] = count
        elif platform == "linkedin":
            self.metrics["social"]["linkedin_connections"] = count
        elif platform == "discord":
            self.metrics["social"]["discord_members"] = count
        elif platform == "newsletter":
            self.metrics["social"]["newsletter_subscribers"] = count
        
        self.save_metrics()
    
    def update_community_metrics(self, active_users: int = None, contributors: int = None, 
                                feedback_count: int = None, partnerships: int = None):
        """Update community metrics"""
        if active_users is not None:
            self.metrics["community"]["active_users"] = active_users
        
        if contributors is not None:
            self.metrics["community"]["contributors"] = contributors
        
        if feedback_count is not None:
            self.metrics["community"]["feedback_count"] = feedback_count
        
        if partnerships is not None:
            self.metrics["community"]["partnerships"] = partnerships
        
        self.save_metrics()
    
    def update_revenue_metrics(self, total_earnings: float = None, 
                              active_paying_users: int = None, mrr: float = None):
        """Update revenue metrics"""
        if total_earnings is not None:
            self.metrics["revenue"]["total_earnings"] = total_earnings
        
        if active_paying_users is not None:
            self.metrics["revenue"]["active_paying_users"] = active_paying_users
        
        if mrr is not None:
            self.metrics["revenue"]["mrr"] = mrr
        
        self.save_metrics()
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        report = {
            "summary": {
                "days_since_start": self._days_since_start(),
                "overall_progress": self._calculate_overall_progress(),
                "key_achievements": self._get_key_achievements()
            },
            "github": {
                "current_stars": self.metrics["github"]["stars"],
                "current_forks": self.metrics["github"]["forks"],
                "star_growth_rate": self._calculate_growth_rate("stars"),
                "fork_growth_rate": self._calculate_growth_rate("forks")
            },
            "website": {
                "total_visitors": self.metrics["website"]["visitors"],
                "total_signups": self.metrics["website"]["signups"],
                "conversion_rate": self.metrics["website"]["conversion_rate"],
                "visitor_growth_rate": self._calculate_visitor_growth()
            },
            "social": {
                "twitter_followers": self.metrics["social"]["twitter_followers"],
                "linkedin_connections": self.metrics["social"]["linkedin_connections"],
                "discord_members": self.metrics["social"]["discord_members"],
                "newsletter_subscribers": self.metrics["social"]["newsletter_subscribers"]
            },
            "community": {
                "active_users": self.metrics["community"]["active_users"],
                "contributors": self.metrics["community"]["contributors"],
                "feedback_count": self.metrics["community"]["feedback_count"],
                "partnerships": self.metrics["community"]["partnerships"]
            },
            "revenue": {
                "total_earnings": self.metrics["revenue"]["total_earnings"],
                "active_paying_users": self.metrics["revenue"]["active_paying_users"],
                "mrr": self.metrics["revenue"]["mrr"]
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _days_since_start(self) -> int:
        """Calculate days since start"""
        start_date = datetime.strptime(self.metrics["start_date"], "%Y-%m-%d")
        current_date = datetime.now()
        return (current_date - start_date).days
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        # Simple weighted average of key metrics
        weights = {
            "github_stars": 0.3,
            "website_signups": 0.2,
            "social_followers": 0.2,
            "community_active": 0.2,
            "revenue": 0.1
        }
        
        progress = 0
        
        # GitHub progress (target: 1000 stars)
        github_progress = min(self.metrics["github"]["stars"] / 1000, 1.0)
        progress += github_progress * weights["github_stars"]
        
        # Website progress (target: 500 signups)
        website_progress = min(self.metrics["website"]["signups"] / 500, 1.0)
        progress += website_progress * weights["website_signups"]
        
        # Social progress (target: 1000 followers)
        social_followers = (self.metrics["social"]["twitter_followers"] + 
                          self.metrics["social"]["linkedin_connections"])
        social_progress = min(social_followers / 1000, 1.0)
        progress += social_progress * weights["social_followers"]
        
        # Community progress (target: 100 active users)
        community_progress = min(self.metrics["community"]["active_users"] / 100, 1.0)
        progress += community_progress * weights["community_active"]
        
        # Revenue progress (target: $1000 MRR)
        revenue_progress = min(self.metrics["revenue"]["mrr"] / 1000, 1.0)
        progress += revenue_progress * weights["revenue"]
        
        return round(progress * 100, 2)
    
    def _get_key_achievements(self) -> List[str]:
        """Get key achievements"""
        achievements = []
        
        if self.metrics["github"]["stars"] >= 100:
            achievements.append("🏆 Reached 100+ GitHub stars")
        
        if self.metrics["website"]["signups"] >= 50:
            achievements.append("🎯 Achieved 50+ demo signups")
        
        if self.metrics["social"]["discord_members"] >= 100:
            achievements.append("👥 Built community of 100+ members")
        
        if self.metrics["community"]["partnerships"] >= 1:
            achievements.append("🤝 Secured first partnership")
        
        if self.metrics["revenue"]["mrr"] > 0:
            achievements.append("💰 Started generating revenue")
        
        return achievements
    
    def _calculate_growth_rate(self, metric: str) -> float:
        """Calculate growth rate for GitHub metrics"""
        if metric == "stars":
            data = self.metrics["github"]["daily_stars"]
        elif metric == "forks":
            data = self.metrics["github"]["daily_forks"]
        else:
            return 0.0
        
        if len(data) < 2:
            return 0.0
        
        # Calculate daily growth rate
        recent = data[-1]["count"]
        previous = data[-2]["count"] if len(data) > 1 else 0
        
        if previous == 0:
            return 100.0 if recent > 0 else 0.0
        
        growth_rate = ((recent - previous) / previous) * 100
        return round(growth_rate, 2)
    
    def _calculate_visitor_growth(self) -> float:
        """Calculate website visitor growth rate"""
        data = self.metrics["website"]["daily_visitors"]
        
        if len(data) < 2:
            return 0.0
        
        recent = data[-1]["count"]
        previous = data[-2]["count"] if len(data) > 1 else 0
        
        if previous == 0:
            return 100.0 if recent > 0 else 0.0
        
        growth_rate = ((recent - previous) / previous) * 100
        return round(growth_rate, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        # GitHub recommendations
        if self.metrics["github"]["stars"] < 50:
            recommendations.append("🚀 Focus on GitHub promotion: Share on Hacker News, Reddit programming communities")
        
        if self.metrics["github"]["forks"] < 10:
            recommendations.append("🔧 Improve documentation: Make it easier for others to contribute")
        
        # Website recommendations
        if self.metrics["website"]["conversion_rate"] < 5.0:
            recommendations.append("🎯 Optimize landing page: Improve call-to-action and value proposition")
        
        if self.metrics["website"]["visitors"] < 100:
            recommendations.append("📢 Increase traffic: Share on social media, engage with relevant communities")
        
        # Social recommendations
        if self.metrics["social"]["twitter_followers"] < 100:
            recommendations.append("🐦 Engage on Twitter: Share updates, join conversations, use relevant hashtags")
        
        if self.metrics["social"]["discord_members"] < 50:
            recommendations.append("👥 Grow community: Invite early users, host events, offer value")
        
        # Community recommendations
        if self.metrics["community"]["feedback_count"] < 10:
            recommendations.append("💬 Collect more feedback: Reach out to users, create feedback forms")
        
        if self.metrics["community"]["contributors"] < 3:
            recommendations.append("🤝 Encourage contributions: Label beginner-friendly issues, offer guidance")
        
        return recommendations

def main():
    """Main function"""
    dashboard = MetricsDashboard()
    
    print("📊 Promotion Metrics Dashboard")
    print("=" * 60)
    
    # Generate report
    report = dashboard.generate_report()
    
    print(f"\n📈 Overall Progress: {report['summary']['overall_progress']}%")
    print(f"📅 Days since start: {report['summary']['days_since_start']}")
    
    print("\n🎯 Key Achievements:")
    for achievement in report['summary']['key_achievements']:
        print(f"  • {achievement}")
    
    print("\n📊 GitHub Metrics:")
    print(f"  • Stars: {report['github']['current_stars']} (Growth: {report['github']['star_growth_rate']}%)")
    print(f"  • Forks: {report['github']['current_forks']} (Growth: {report['github']['fork_growth_rate']}%)")
    
    print("\n🌐 Website Metrics:")
    print(f"  • Visitors: {report['website']['total_visitors']}")
    print(f"  • Signups: {report['website']['total_signups']}")
    print(f"  • Conversion: {report['website']['conversion_rate']}%")
    
    print("\n👥 Social Metrics:")
    print(f"  • Twitter: {report['social']['twitter_followers']} followers")
    print(f"  • LinkedIn: {report['social']['linkedin_connections']} connections")
    print(f"  • Discord: {report['social']['discord_members']} members")
    print(f"  • Newsletter: {report['social']['newsletter_subscribers']} subscribers")
    
    print("\n💡 Recommendations:")
    for recommendation in report['recommendations']:
        print(f"  • {recommendation}")
    
    # Save report
    with open("promotion_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to 'promotion_report.json'")
    print("\n📋 Next Steps:")
    print("1. Update metrics regularly using the dashboard methods")
    print("2. Review recommendations and implement improvements")
    print("3. Track progress towards your goals")

if __name__ == "__main__":
    main()