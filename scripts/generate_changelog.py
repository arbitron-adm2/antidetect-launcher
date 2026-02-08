#!/usr/bin/env python3
"""Generate changelog from git commits for release."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_commits_since_last_tag():
    """Get commits since last tag."""
    try:
        # Get previous tag
        prev_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        # No previous tag, get all commits
        prev_tag = None

    # Get commits
    if prev_tag:
        cmd = ["git", "log", f"{prev_tag}..HEAD", "--pretty=format:%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%s"]

    commits = subprocess.check_output(cmd).decode().strip().split("\n")
    return commits


def categorize_commits(commits):
    """Categorize commits by type."""
    categories = {
        "Features": [],
        "Bug Fixes": [],
        "Performance": [],
        "Documentation": [],
        "Refactoring": [],
        "Tests": [],
        "Chores": [],
        "Other": []
    }

    for commit in commits:
        commit = commit.strip()
        if not commit:
            continue

        lower_commit = commit.lower()

        if any(x in lower_commit for x in ["feat:", "feature:", "add:"]):
            categories["Features"].append(commit)
        elif any(x in lower_commit for x in ["fix:", "bug:", "bugfix:"]):
            categories["Bug Fixes"].append(commit)
        elif any(x in lower_commit for x in ["perf:", "performance:", "optimize:"]):
            categories["Performance"].append(commit)
        elif any(x in lower_commit for x in ["docs:", "doc:", "documentation:"]):
            categories["Documentation"].append(commit)
        elif any(x in lower_commit for x in ["refactor:", "refactoring:"]):
            categories["Refactoring"].append(commit)
        elif any(x in lower_commit for x in ["test:", "tests:"]):
            categories["Tests"].append(commit)
        elif any(x in lower_commit for x in ["chore:", "build:", "ci:"]):
            categories["Chores"].append(commit)
        else:
            categories["Other"].append(commit)

    return categories


def generate_changelog(version):
    """Generate changelog for version."""
    commits = get_commits_since_last_tag()
    categories = categorize_commits(commits)

    # Generate markdown
    changelog = [
        f"# Release v{version}",
        "",
        f"Released on {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ]

    for category, items in categories.items():
        if items:
            changelog.append(f"## {category}")
            changelog.append("")
            for item in items:
                # Clean up commit message
                item = item.split(":", 1)[-1].strip()
                changelog.append(f"- {item}")
            changelog.append("")

    # Add installation instructions
    changelog.extend([
        "## Installation",
        "",
        "### Windows",
        "Download and run `AntidetectBrowser-Setup-{version}.exe`",
        "",
        "### Linux",
        "```bash",
        f"sudo dpkg -i antidetect-browser_{version}_amd64.deb",
        "sudo apt-get install -f",
        "```",
        "",
        "### macOS",
        f"Download and open `AntidetectBrowser-macOS-{version}.dmg`",
        "",
        "## What's Changed",
        "See full diff at https://github.com/antidetect/antidetect-playwright/compare/v{prev}...v{version}",
        ""
    ])

    return "\n".join(changelog)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_changelog.py VERSION")
        sys.exit(1)

    version = sys.argv[1]
    changelog = generate_changelog(version)
    print(changelog)
