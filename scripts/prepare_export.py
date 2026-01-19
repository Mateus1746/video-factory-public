#!/usr/bin/env python3
"""
YouTube Factory Sync Script
This script prepares the `youtube_factory` folder for GitHub export.
It copies all projects from `youtube/mvp` to `youtube/youtube_factory/mvp`.
"""
import os
import shutil
import subprocess
import argparse
from pathlib import Path

# Paths - Adjusted to be relative or absolute based on execution
# We assume this script runs from correct location or we use absolute paths
BASE_DIR = Path("/home/mateus/projetos/orquestrador/youtube")
SOURCE_MVP = BASE_DIR / "mvp"
FACTORY_ROOT = BASE_DIR / "youtube_factory"
FACTORY_MVP = FACTORY_ROOT / "mvp"

IGNORE_PATTERNS = shutil.ignore_patterns(
    "__pycache__", 
    ".git", 
    ".venv", 
    "*.mp4", 
    "*.avi", 
    "*.mkv", 
    "output_render", 
    "batch_output"
)

def setup_directories():
    """Ensure clean destination structure."""
    if not FACTORY_ROOT.exists():
        print(f"Creating factory root: {FACTORY_ROOT}")
        FACTORY_ROOT.mkdir(parents=True)
    
    # We don't delete the root, just the MVP folder to avoid deleting .git or workflows
    if FACTORY_MVP.exists():
        print(f"Cleaning existing MVP mirror: {FACTORY_MVP}")
        shutil.rmtree(FACTORY_MVP)
    
    print(f"Creating new MVP mirror: {FACTORY_MVP}")
    FACTORY_MVP.mkdir()

def copy_projects():
    """Copy all projects from source to destination."""
    print("🚀 Copying projects...")
    
    if not SOURCE_MVP.exists():
        print(f"❌ Error: Source folder {SOURCE_MVP} does not exist!")
        return

    for item in SOURCE_MVP.iterdir():
        if item.is_dir() and not item.name.startswith(('.', '__')):
            dest = FACTORY_MVP / item.name
            print(f"  -> Copying {item.name}...")
            shutil.copytree(item, dest, ignore=IGNORE_PATTERNS)
            
    print("✅ All projects copied.")

def git_automator():
    """Auto-push to GitHub if requested."""
    # Check if inside a git repo
    if not (FACTORY_ROOT / ".git").exists():
        print("⚠ Factory folder is not a git repository yet. Run 'git init' inside it first.")
        return

    print("🤖 Running Git Automation...")
    try:
        subprocess.run(["git", "add", "."], cwd=FACTORY_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "Auto-sync from Orchestrator"], cwd=FACTORY_ROOT, check=True)
        subprocess.run(["git", "push"], cwd=FACTORY_ROOT, check=True)
        print("🚀 Successfully pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Sync Orchestrator MVPs to GitHub Factory")
    parser.add_argument("--push", action="store_true", help="Automatically git add/commit/push after syncing")
    args = parser.parse_args()

    setup_directories()
    copy_projects()
    
    if args.push:
        git_automator()
    else:
        print("\n✅ Sync complete. Go to 'youtube/youtube_factory' and run git commands manually.")

if __name__ == "__main__":
    main()
