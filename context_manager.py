#!/usr/bin/env python3
"""
Context Manager for AI Assistant Sessions
Saves and loads context between sessions
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ContextManager:
    def __init__(self, context_file=".ai_context.json"):
        self.context_file = Path(context_file)
        self.context = self.load_context()
    
    def load_context(self):
        """Load context from file"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._default_context()
        return self._default_context()
    
    def save_context(self):
        """Save context to file"""
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def _default_context(self):
        """Return default context structure"""
        return {
            "project": {
                "name": "",
                "description": "",
                "tech_stack": [],
                "current_task": "",
                "next_steps": []
            },
            "session": {
                "last_updated": datetime.now().isoformat(),
                "recent_changes": [],
                "issues_encountered": [],
                "solutions_found": []
            },
            "files": {
                "important_paths": [],
                "recently_edited": []
            },
            "git": {
                "last_commit": "",
                "branch": "",
                "pending_changes": []
            }
        }
    
    def update_project_info(self, **kwargs):
        """Update project information"""
        self.context["project"].update(kwargs)
        self.context["session"]["last_updated"] = datetime.now().isoformat()
        self.save_context()
    
    def add_recent_change(self, change):
        """Add a recent change to context"""
        self.context["session"]["recent_changes"].append({
            "timestamp": datetime.now().isoformat(),
            "change": change
        })
        # Keep only last 10 changes
        self.context["session"]["recent_changes"] = self.context["session"]["recent_changes"][-10:]
        self.save_context()
    
    def add_issue(self, issue, solution=""):
        """Add an issue encountered"""
        self.context["session"]["issues_encountered"].append({
            "timestamp": datetime.now().isoformat(),
            "issue": issue,
            "solution": solution
        })
        self.save_context()
    
    def get_summary(self):
        """Get a human-readable summary"""
        summary = []
        summary.append(f"=== PROJECT: {self.context['project'].get('name', 'Unknown')} ===")
        summary.append(f"Description: {self.context['project'].get('description', '')}")
        summary.append(f"Current Task: {self.context['project'].get('current_task', '')}")
        
        if self.context['project'].get('next_steps'):
            summary.append("\nNext Steps:")
            for i, step in enumerate(self.context['project']['next_steps'], 1):
                summary.append(f"  {i}. {step}")
        
        if self.context['session']['recent_changes']:
            summary.append("\nRecent Changes:")
            for change in self.context['session']['recent_changes'][-3:]:
                summary.append(f"  • {change['change']}")
        
        if self.context['session']['issues_encountered']:
            summary.append("\nRecent Issues:")
            for issue in self.context['session']['issues_encountered'][-3:]:
                summary.append(f"  • {issue['issue']}")
                if issue['solution']:
                    summary.append(f"    Solution: {issue['solution']}")
        
        return "\n".join(summary)

# Quick usage functions
def save_context(project_name="", current_task="", next_steps=None, recent_change=""):
    """Quick function to save context"""
    cm = ContextManager()
    if project_name:
        cm.update_project_info(name=project_name)
    if current_task:
        cm.update_project_info(current_task=current_task)
    if next_steps:
        cm.update_project_info(next_steps=next_steps)
    if recent_change:
        cm.add_recent_change(recent_change)
    return cm.get_summary()

def load_context():
    """Quick function to load and display context"""
    cm = ContextManager()
    return cm.get_summary()

if __name__ == "__main__":
    # Example usage
    print("Context Manager Ready")
    print("\nCurrent Context:")
    print(load_context())