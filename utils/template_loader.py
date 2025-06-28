"""
Template loader utility for q2JSON
"""
import os
from pathlib import Path

def load_template(template_name):
    """Load template file content"""
    template_path = Path(__file__).parent.parent / "templates" / template_name
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Template {template_name} not found"

def get_available_templates():
    """Get list of available templates"""
    template_dir = Path(__file__).parent.parent / "templates"
    if template_dir.exists():
        return [f.name for f in template_dir.glob("*.txt")]
    return []
