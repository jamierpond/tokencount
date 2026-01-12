#!/bin/bash
set -e

if [[ $# -ne 1 ]] || [[ ! "$1" =~ ^(major|minor|patch)$ ]]; then
    echo "Usage: $0 <major|minor|patch>"
    exit 1
fi

BUMP_TYPE=$1
PYPROJECT="pyproject.toml"

# Extract current version
CURRENT=$(grep '^version = ' "$PYPROJECT" | head -1 | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$CURRENT" ]]; then
    echo "Could not find version in $PYPROJECT"
    exit 1
fi

# Parse semver
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Bump
case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW="$MAJOR.$MINOR.$PATCH"

# Update pyproject.toml
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" "$PYPROJECT"

echo "$CURRENT -> $NEW"

# Commit
git add "$PYPROJECT"
git commit -m "chore: bump to v$NEW"

echo "Committed: chore: bump to v$NEW"
