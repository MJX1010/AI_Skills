#!/usr/bin/env python3
"""
Skill packaging script
Validates and packages a skill into a .skill file
"""

import os
import sys
import re
import zipfile
import argparse
from pathlib import Path

def validate_frontmatter(skill_md_content: str) -> tuple:
    """Validate YAML frontmatter in SKILL.md"""
    errors = []
    
    # Check for frontmatter
    if not skill_md_content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors
    
    # Extract frontmatter
    parts = skill_md_content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter format")
        return False, errors
    
    frontmatter = parts[1].strip()
    
    # Check for required fields
    if "name:" not in frontmatter:
        errors.append("Missing required field: name")
    
    if "description:" not in frontmatter:
        errors.append("Missing required field: description")
    
    return len(errors) == 0, errors

def validate_skill_name(name: str) -> tuple:
    """Validate skill name format"""
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "Skill name must contain only lowercase letters, digits, and hyphens"
    if len(name) > 64:
        return False, "Skill name must be 64 characters or less"
    return True, None

def check_symlinks(skill_dir: Path) -> list:
    """Check for symlinks in skill directory"""
    symlinks = []
    for item in skill_dir.rglob("*"):
        if item.is_symlink():
            symlinks.append(str(item.relative_to(skill_dir)))
    return symlinks

def validate_skill(skill_dir: Path) -> tuple:
    """Validate a skill directory"""
    errors = []
    
    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors
    
    # Read SKILL.md
    content = skill_md.read_text()
    
    # Validate frontmatter
    valid, fm_errors = validate_frontmatter(content)
    if not valid:
        errors.extend(fm_errors)
    
    # Check for symlinks
    symlinks = check_symlinks(skill_dir)
    if symlinks:
        errors.append(f"Symlinks found (not allowed): {', '.join(symlinks)}")
    
    return len(errors) == 0, errors

def package_skill(skill_dir: Path, output_dir: Path = None):
    """Package a skill into a .skill file"""
    
    # Validate first
    valid, errors = validate_skill(skill_dir)
    if not valid:
        print("❌ Validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    # Determine output path
    skill_name = skill_dir.name
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = skill_dir.parent
    
    output_file = output_dir / f"{skill_name}.skill"
    
    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in skill_dir.rglob("*"):
            if item.is_file():
                arcname = item.relative_to(skill_dir)
                zf.write(item, arcname)
    
    print(f"✅ Packaged: {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Package a skill")
    parser.add_argument("skill_dir", help="Path to skill directory")
    parser.add_argument("output_dir", nargs="?", help="Optional output directory")
    
    args = parser.parse_args()
    
    skill_dir = Path(args.skill_dir)
    if not skill_dir.exists():
        print(f"❌ Skill directory not found: {skill_dir}")
        sys.exit(1)
    
    success = package_skill(skill_dir, args.output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
