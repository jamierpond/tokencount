#!/bin/bash
set -e

PYPROJECT="pyproject.toml"

# Extract current version
VERSION=$(grep '^version = ' "$PYPROJECT" | head -1 | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$VERSION" ]]; then
    echo "Could not find version in $PYPROJECT"
    exit 1
fi

TAG="v$VERSION"

echo "Creating tag: $TAG"
git tag "$TAG"

echo ""
git show "$TAG" --quiet
echo ""

read -p "Push $TAG to origin? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin HEAD "$TAG"
    echo "Pushed commit and $TAG"
else
    git tag -d "$TAG"
    echo "Cancelled. Tag deleted."
fi
