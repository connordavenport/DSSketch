#!/bin/bash

# DSSketch Version Helper Scripts
# Source this file to get convenient versioning commands

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show current version
version-show() {
    local current_version=$(grep "current_version" .bumpversion.cfg 2>/dev/null | cut -d' ' -f3)
    if [ -n "$current_version" ]; then
        echo -e "${GREEN}📦 Current version: ${BLUE}$current_version${NC}"
    else
        echo -e "${RED}❌ Could not find version in .bumpversion.cfg${NC}"
    fi
}

# Function to manually bump patch version
version-patch() {
    echo -e "${YELLOW}📈 Manually bumping patch version...${NC}"
    bump2version patch --allow-dirty
    version-show
}

# Function to manually bump minor version  
version-minor() {
    echo -e "${YELLOW}📈 Manually bumping minor version...${NC}"
    bump2version minor --allow-dirty
    version-show
}

# Function to manually bump major version
version-major() {
    echo -e "${YELLOW}📈 Manually bumping major version...${NC}"
    bump2version major --allow-dirty
    version-show
}

# Function to commit with automatic version bump (bypass hook if needed)
git-commit-nobump() {
    echo -e "${YELLOW}📝 Committing without version bump...${NC}"
    git commit --no-verify "$@"
}

# Function to show version history
version-history() {
    echo -e "${BLUE}📚 Version history:${NC}"
    git tag --sort=-version:refname | head -10
}

# Function to show help
version-help() {
    echo -e "${BLUE}🔧 DSSketch Version Helper Commands:${NC}"
    echo -e "  ${GREEN}version-show${NC}     - Show current version"
    echo -e "  ${GREEN}version-patch${NC}    - Manually bump patch (Z)"
    echo -e "  ${GREEN}version-minor${NC}    - Manually bump minor (Y)"  
    echo -e "  ${GREEN}version-major${NC}    - Manually bump major (X)"
    echo -e "  ${GREEN}version-history${NC}  - Show recent version tags"
    echo -e "  ${GREEN}git-commit-nobump${NC} - Commit without auto version bump"
    echo -e ""
    echo -e "${YELLOW}📋 Automatic versioning:${NC}"
    echo -e "  • ${GREEN}git commit${NC} - Auto-bumps patch version (Z)"
    echo -e "  • ${GREEN}git merge to main${NC} - Auto-bumps minor version (Y)"
}

# Show help on load
version-help