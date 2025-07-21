#!/bin/bash

# Git Issue Diagnostic Script
echo "🔍 Git Issue Diagnostic Report"
echo "================================"

# Check current directory
echo "📁 Current Directory: $(pwd)"
echo ""

# Check if we're in a git repository
if [ -d ".git" ]; then
    echo "✅ Git repository found"
else
    echo "❌ Not in a git repository"
    exit 1
fi

# Check git status
echo ""
echo "🔍 Git Status:"
git status

# Check recent commits
echo ""
echo "📜 Recent Commits:"
git log --oneline -5

# Check if files are different from last commit
echo ""
echo "🔍 Files Changed Since Last Commit:"
git diff --name-only HEAD

# Check if there are untracked files
echo ""
echo "📦 Untracked Files:"
git ls-files --others --exclude-standard

# Check if there are modified files
echo ""
echo "✏️  Modified Files:"
git diff --name-only

# Check if there are staged files
echo ""
echo "📋 Staged Files:"
git diff --cached --name-only

echo ""
echo "🔍 Diagnostic Complete!" 