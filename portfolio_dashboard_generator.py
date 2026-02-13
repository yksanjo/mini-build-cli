#!/usr/bin/env python3
"""
Portfolio Dashboard Generator
Creates an interactive HTML dashboard from GitHub portfolio analysis data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class DashboardGenerator:
    """Generates interactive HTML dashboard"""
    
    def __init__(self, data_file: str = "portfolio_summary.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load portfolio summary data"""
        if not os.path.exists(self.data_file):
            return {}
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def generate_dashboard(self, output_file: str = "portfolio_dashboard.html"):
        """Generate complete HTML dashboard"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.data.get('username', 'GitHub')} Portfolio Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e293b;
            --gray: #64748b;
            --light-gray: #f1f5f9;
            --card-bg: #ffffff;
            --body-bg: #f8fafc;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: var(--body-bg);
            color: var(--dark);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card .icon {{
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .stat-card.primary .icon {{ background: rgba(99, 102, 241, 0.1); color: var(--primary); }}
        .stat-card.success .icon {{ background: rgba(34, 197, 94, 0.1); color: var(--success); }}
        .stat-card.warning .icon {{ background: rgba(245, 158, 11, 0.1); color: var(--warning); }}
        .stat-card.secondary .icon {{ background: rgba(236, 72, 153, 0.1); color: var(--secondary); }}
        
        .stat-card h3 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        
        .stat-card p {{
            color: var(--gray);
            font-size: 0.9rem;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .card h2 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .card h2 i {{
            color: var(--primary);
        }}
        
        .insight-item {{
            padding: 1rem;
            border-left: 3px solid var(--primary);
            background: var(--light-gray);
            border-radius: 0 0.5rem 0.5rem 0;
            margin-bottom: 1rem;
        }}
        
        .insight-item h4 {{
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        
        .insight-item p {{
            font-size: 0.9rem;
            color: var(--gray);
            margin-bottom: 0.5rem;
        }}
        
        .score-bar {{
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .score-bar .fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 4px;
            transition: width 1s ease;
        }}
        
        .repo-card {{
            display: flex;
            align-items: start;
            gap: 1rem;
            padding: 1rem;
            background: var(--light-gray);
            border-radius: 0.75rem;
            margin-bottom: 0.75rem;
            transition: background 0.2s;
        }}
        
        .repo-card:hover {{
            background: #e2e8f0;
        }}
        
        .repo-rank {{
            width: 32px;
            height: 32px;
            background: var(--primary);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.875rem;
            flex-shrink: 0;
        }}
        
        .repo-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .repo-info h4 {{
            font-weight: 600;
            margin-bottom: 0.25rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .repo-info p {{
            font-size: 0.85rem;
            color: var(--gray);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .repo-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.8rem;
            color: var(--gray);
            margin-top: 0.5rem;
        }}
        
        .repo-meta span {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}
        
        .repo-score {{
            text-align: right;
        }}
        
        .repo-score .score {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .repo-score .label {{
            font-size: 0.75rem;
            color: var(--gray);
        }}
        
        .language-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.75rem;
            background: white;
            border-radius: 9999px;
            font-size: 0.8rem;
            margin: 0.25rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        .language-tag .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        
        .trend-year {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .trend-year:last-child {{
            border-bottom: none;
        }}
        
        .trend-year .year {{
            font-weight: 600;
            min-width: 50px;
        }}
        
        .trend-year .count {{
            background: var(--primary);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .trend-year .details {{
            font-size: 0.85rem;
            color: var(--gray);
        }}
        
        .recommendation {{
            padding: 0.75rem 1rem;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            display: flex;
            align-items: start;
            gap: 0.5rem;
        }}
        
        .recommendation i {{
            color: var(--primary);
            margin-top: 0.2rem;
        }}
        
        .chart-container {{
            position: relative;
            height: 250px;
            margin-top: 1rem;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--gray);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            header h1 {{
                font-size: 1.75rem;
            }}
            
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        
        {self._generate_stats_grid()}
        
        <div class="dashboard-grid">
            {self._generate_insights_card()}
            {self._generate_showcase_card()}
            {self._generate_languages_card()}
            {self._generate_trends_card()}
        </div>
        
        {self._generate_recommendations()}
        
        <footer>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} • 
            <a href="https://github.com/{self.data.get('username', '')}" target="_blank" style="color: var(--primary);">
                View GitHub Profile <i class="fas fa-external-link-alt"></i>
            </a></p>
        </footer>
    </div>
    
    {self._generate_charts_script()}
</body>
</html>"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✅ Dashboard generated: {output_file}")
        return output_file
    
    def _generate_header(self) -> str:
        """Generate header section"""
        username = self.data.get('username', 'Developer')
        total = self.data.get('total_repos', 0)
        
        return f"""
        <header>
            <h1><i class="fab fa-github"></i> {username}'s Portfolio</h1>
            <p>Comprehensive analysis of {total} repositories • Coding journey visualization</p>
        </header>
        """
    
    def _generate_stats_grid(self) -> str:
        """Generate top stats cards"""
        insights = self.data.get('insights', [])
        
        # Find relevant insights
        portfolio_health = next((i for i in insights if i['category'] == 'Portfolio Health'), {})
        engagement = next((i for i in insights if i['category'] == 'Community Engagement'), {})
        tech_stack = next((i for i in insights if i['category'] == 'Tech Stack'), {})
        showcase = next((i for i in insights if i['category'] == 'Showcase Quality'), {})
        
        # Extract numbers
        total_repos = self.data.get('total_repos', 0)
        total_stars = sum(r.get('stars', 0) for r in self.data.get('showcase_recommendations', []))
        
        lang_dist = self.data.get('language_distribution', {})
        total_langs = len(lang_dist)
        
        return f"""
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="icon"><i class="fas fa-code-branch"></i></div>
                <h3>{total_repos}</h3>
                <p>Total Repositories</p>
            </div>
            <div class="stat-card success">
                <div class="icon"><i class="fas fa-star"></i></div>
                <h3>{total_stars}</h3>
                <p>Total Stars</p>
            </div>
            <div class="stat-card warning">
                <div class="icon"><i class="fas fa-layer-group"></i></div>
                <h3>{total_langs}</h3>
                <p>Languages Used</p>
            </div>
            <div class="stat-card secondary">
                <div class="icon"><i class="fas fa-trophy"></i></div>
                <h3>{showcase.get('score', 0):.0f}/100</h3>
                <p>Showcase Score</p>
            </div>
        </div>
        """
    
    def _generate_insights_card(self) -> str:
        """Generate insights card"""
        insights = self.data.get('insights', [])[:4]  # Top 4 insights
        
        insights_html = ""
        for insight in insights:
            score = insight.get('score', 0)
            bar_width = min(100, max(0, score))
            
            insights_html += f"""
            <div class="insight-item">
                <h4>{insight['category']}</h4>
                <p>{insight['title']}</p>
                <div class="score-bar">
                    <div class="fill" style="width: {bar_width}%"></div>
                </div>
            </div>
            """
        
        return f"""
        <div class="card">
            <h2><i class="fas fa-lightbulb"></i> Portfolio Insights</h2>
            {insights_html}
        </div>
        """
    
    def _generate_showcase_card(self) -> str:
        """Generate top projects showcase"""
        showcase = self.data.get('showcase_recommendations', [])[:5]
        
        repos_html = ""
        for i, repo in enumerate(showcase, 1):
            desc = repo.get('description', 'No description')
            if desc and len(desc) > 60:
                desc = desc[:60] + "..."
            
            repos_html += f"""
            <div class="repo-card">
                <div class="repo-rank">{i}</div>
                <div class="repo-info">
                    <h4>{repo['name']}</h4>
                    <p>{desc or 'No description available'}</p>
                    <div class="repo-meta">
                        <span><i class="fas fa-star"></i> {repo['stars']}</span>
                        <span><i class="fas fa-code-branch"></i> {repo['forks']}</span>
                        <span><i class="fas fa-circle" style="color: {self._get_language_color(repo.get('primary_language', ''))}"></i> {repo.get('primary_language', 'N/A')}</span>
                    </div>
                </div>
                <div class="repo-score">
                    <div class="score">{repo['showcase_score']:.0f}</div>
                    <div class="label">score</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="card">
            <h2><i class="fas fa-trophy"></i> Top Projects to Showcase</h2>
            {repos_html}
        </div>
        """
    
    def _generate_languages_card(self) -> str:
        """Generate language distribution card"""
        lang_dist = self.data.get('language_distribution', {})
        
        # Sort by count
        sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:8]
        
        # Generate tags
        tags_html = ""
        for lang, count in sorted_langs:
            color = self._get_language_color(lang)
            tags_html += f"""
            <span class="language-tag">
                <span class="dot" style="background: {color}"></span>
                {lang} ({count})
            </span>
            """
        
        # Chart data
        labels = [l[0] for l in sorted_langs[:6]]
        data = [l[1] for l in sorted_langs[:6]]
        colors = [self._get_language_color(l) for l in labels]
        
        return f"""
        <div class="card">
            <h2><i class="fas fa-code"></i> Language Distribution</h2>
            <div style="margin-bottom: 1rem;">
                {tags_html}
            </div>
            <div class="chart-container">
                <canvas id="languageChart"></canvas>
            </div>
            <script>
                new Chart(document.getElementById('languageChart'), {{
                    type: 'doughnut',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            data: {json.dumps(data)},
                            backgroundColor: {json.dumps(colors)},
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'right',
                                labels: {{ boxWidth: 12 }}
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
        """
    
    def _generate_trends_card(self) -> str:
        """Generate coding trends card"""
        trends = self.data.get('coding_trends', {})
        
        # Sort by year
        sorted_years = sorted(trends.items(), key=lambda x: x[0], reverse=True)[:5]
        
        trends_html = ""
        for year, data in sorted_years:
            count = data.get('count', 0)
            langs = list(data.get('languages', {}).keys())[:3]
            lang_str = ', '.join(langs) if langs else 'N/A'
            
            trends_html += f"""
            <div class="trend-year">
                <span class="year">{year}</span>
                <span class="count">{count}</span>
                <span class="details">{lang_str}</span>
            </div>
            """
        
        # Prepare chart data
        years = [y[0] for y in sorted(sorted_years, key=lambda x: x[0])]
        counts = [trends[y].get('count', 0) for y in years]
        
        return f"""
        <div class="card">
            <h2><i class="fas fa-chart-line"></i> Coding Activity</h2>
            {trends_html}
            <div class="chart-container" style="margin-top: 1.5rem;">
                <canvas id="trendsChart"></canvas>
            </div>
            <script>
                new Chart(document.getElementById('trendsChart'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(years)},
                        datasets: [{{
                            label: 'Repositories Created',
                            data: {json.dumps(counts)},
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{ stepSize: 1 }}
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
        """
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section"""
        insights = self.data.get('insights', [])
        
        all_recommendations = []
        for insight in insights:
            all_recommendations.extend(insight.get('recommendations', []))
        
        if not all_recommendations:
            return ""
        
        recs_html = ""
        for rec in all_recommendations[:5]:  # Top 5
            recs_html += f"""
            <div class="recommendation">
                <i class="fas fa-info-circle"></i>
                <span>{rec}</span>
            </div>
            """
        
        return f"""
        <div class="card" style="margin-top: 1.5rem;">
            <h2><i class="fas fa-wand-magic-sparkles"></i> Recommendations</h2>
            {recs_html}
        </div>
        """
    
    def _generate_charts_script(self) -> str:
        """Generate additional chart scripts if needed"""
        return "<!-- Charts initialized inline -->"
    
    def _get_language_color(self, lang: str) -> str:
        """Get color for programming language"""
        colors = {
            'python': '#3776ab',
            'javascript': '#f7df1e',
            'typescript': '#3178c6',
            'html': '#e34c26',
            'css': '#1572b6',
            'java': '#b07219',
            'go': '#00add8',
            'rust': '#dea584',
            'c++': '#f34b7d',
            'c': '#555555',
            'ruby': '#701516',
            'php': '#4f5d95',
            'swift': '#ffac45',
            'kotlin': '#a97bff',
            'shell': '#89e051',
            'jupyter': '#da5b0b',
            'vue': '#41b883',
            'react': '#61dafb',
        }
        return colors.get(lang.lower(), '#6366f1')


def main():
    generator = DashboardGenerator()
    
    if not generator.data:
        print("❌ No portfolio data found. Run github_portfolio_analyzer.py first.")
        return
    
    output = generator.generate_dashboard()
    print(f"\n🚀 Open {output} in your browser to view your portfolio dashboard!")


if __name__ == "__main__":
    main()
