#!/usr/bin/env python3
"""
Skill initialization script
Creates a new skill directory with proper structure
"""

import os
import sys
import argparse
from pathlib import Path

SKILL_TEMPLATE = '''---
name: {skill_name}
description: {description}
---

# {skill_name}

TODO: Write skill description and instructions here

## Quick Start

TODO: Add quick start guide

## Usage

TODO: Add usage instructions
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example script for {skill_name}
"""

def main():
    print("Hello from {skill_name}!")

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = '''# Reference Documentation

TODO: Add reference documentation for {skill_name}
'''

EXAMPLE_ASSET_README = '''# Assets

This directory contains assets for {skill_name}
'''

def create_skill(skill_name: str, output_path: str, resources: list = None, examples: bool = False):
    """Create a new skill directory with template files"""
    
    # Create skill directory
    skill_dir = Path(output_path) / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(SKILL_TEMPLATE.format(
        skill_name=skill_name,
        description=f"TODO: Add description for {skill_name}"
    ))
    
    # Create resource directories if requested
    if resources:
        if "scripts" in resources:
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            if examples:
                example_script = scripts_dir / "example.py"
                example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
                example_script.chmod(0o755)
        
        if "references" in resources:
            ref_dir = skill_dir / "references"
            ref_dir.mkdir(exist_ok=True)
            if examples:
                example_ref = ref_dir / "example.md"
                example_ref.write_text(EXAMPLE_REFERENCE.format(skill_name=skill_name))
        
        if "assets" in resources:
            assets_dir = skill_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            if examples:
                readme = assets_dir / "README.md"
                readme.write_text(EXAMPLE_ASSET_README.format(skill_name=skill_name))
    
    print(f"✅ Created skill: {skill_dir}")
    print(f"   SKILL.md: {skill_md}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")

def main():
    parser = argparse.ArgumentParser(description="Initialize a new skill")
    parser.add_argument("skill_name", help="Name of the skill")
    parser.add_argument("--path", required=True, help="Output directory path")
    parser.add_argument("--resources", help="Comma-separated list: scripts,references,assets")
    parser.add_argument("--examples", action="store_true", help="Add example files")
    
    args = parser.parse_args()
    
    resources = None
    if args.resources:
        resources = [r.strip() for r in args.resources.split(",")]
    
    create_skill(args.skill_name, args.path, resources, args.examples)

if __name__ == "__main__":
    main()
