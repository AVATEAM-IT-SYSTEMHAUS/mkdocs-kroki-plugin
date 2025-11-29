#!/usr/bin/env python3
"""
Release script for mkdocs-kroki-plugin.

Usage: python release.py <version>
Example: python release.py 1.2.3

This script will:
1. Validate the version format
2. Check that the working tree is clean
3. Update the __version__ in kroki/__init__.py
4. Commit the version change
5. Create an annotated git tag
6. Push the commit and tag to origin
7. Open the browser to create a GitHub release
"""

import argparse
import re
import subprocess
import sys
import webbrowser
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture_output, text=True, check=check
    )
    return result


def validate_version(version):
    """Validate that version follows semantic versioning (X.Y.Z)."""
    pattern = r"^\d+\.\d+\.\d+$"
    return re.match(pattern, version) is not None


def check_git_repo():
    """Verify we're in a git repository."""
    result = run_command("git rev-parse --git-dir", check=False)
    if result.returncode != 0:
        print("❌ Error: Not in a git repository")
        sys.exit(1)
    print("✓ In git repository")


def check_clean_tree():
    """Verify the working tree is clean."""
    result = run_command("git status --porcelain")
    if result.stdout.strip():
        print("❌ Error: Working tree has uncommitted changes")
        print("Please commit or stash your changes first")
        sys.exit(1)
    print("✓ Working tree is clean")


def get_github_repo():
    """Extract GitHub org/repo from git remote."""
    result = run_command("git remote get-url origin")
    url = result.stdout.strip()

    # Parse SSH format: git@github.com:org/repo.git
    ssh_match = re.match(r"git@github\.com:(.+)/(.+)\.git", url)
    if ssh_match:
        return f"{ssh_match.group(1)}/{ssh_match.group(2)}"

    # Parse HTTPS format: https://github.com/org/repo.git
    https_match = re.match(r"https://github\.com/(.+)/(.+)\.git", url)
    if https_match:
        return f"{https_match.group(1)}/{https_match.group(2)}"

    print(f"❌ Error: Could not parse GitHub repository from: {url}")
    sys.exit(1)


def update_version_file(version):
    """Update __version__ in kroki/__init__.py."""
    version_file = Path("kroki/__init__.py")

    if not version_file.exists():
        print(f"❌ Error: {version_file} not found")
        sys.exit(1)

    content = version_file.read_text()
    pattern = r'__version__ = ["\']([^"\']+)["\']'
    replacement = f'__version__ = "{version}"'

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print(f"❌ Error: Could not find __version__ in {version_file}")
        sys.exit(1)

    version_file.write_text(new_content)
    print(f"✓ Updated {version_file}")


def create_commit(version):
    """Create a commit with the version change."""
    run_command("git add kroki/__init__.py")
    commit_msg = f"chore: Bump version to {version}"
    run_command(f'git commit -m "{commit_msg}"')
    print(f"✓ Created commit: {commit_msg}")


def create_tag(version):
    """Create an annotated git tag."""
    tag_name = f"v{version}"
    tag_msg = f"Release v{version}"
    run_command(f'git tag -a {tag_name} -m "{tag_msg}"')
    print(f"✓ Created tag: {tag_name}")


def push_to_remote(version):
    """Push commit and tag to origin."""
    # Push the commit
    run_command("git push origin HEAD")
    print("✓ Pushed commit to origin")

    # Push the tag
    tag_name = f"v{version}"
    run_command(f"git push origin {tag_name}")
    print(f"✓ Pushed tag {tag_name} to origin")


def open_release_page(version, repo):
    """Open browser to GitHub release creation page."""
    tag_name = f"v{version}"
    url = f"https://github.com/{repo}/releases/new?tag={tag_name}"

    print(f"\n🎉 Release v{version} ready!\n")
    print("Opening browser to create GitHub release...")

    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Note: Could not open browser automatically: {e}")

    print(f"GitHub Release URL: {url}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new release for mkdocs-kroki-plugin"
    )
    parser.add_argument(
        "version", help="Version number (semantic versioning format: X.Y.Z)"
    )

    args = parser.parse_args()
    version = args.version

    # Validate version format
    if not validate_version(version):
        print(f"❌ Error: Invalid version format: {version}")
        print("Version must follow semantic versioning (X.Y.Z)")
        sys.exit(1)
    print(f"✓ Version {version} is valid")

    # Pre-flight checks
    check_git_repo()
    check_clean_tree()
    repo = get_github_repo()

    # Update version
    update_version_file(version)

    # Create commit and tag
    create_commit(version)
    create_tag(version)

    # Push to remote
    push_to_remote(version)

    # Open release page
    open_release_page(version, repo)


if __name__ == "__main__":
    main()
