#!/usr/bin/env bash
set -euo pipefail

# Immediately exit if REPO_ROOT is not set
if [ -z "$REPO_ROOT" ]; then
    echo "Error: REPO_ROOT is not set. Run this script from the Nix devShell."
    exit 1
fi
cd "$REPO_ROOT"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Supported architectures from flake.nix
declare -A SUPPORTED_ARCHS=(
    ["x86_64-linux"]="Linux x86_64"
    ["aarch64-linux"]="Linux aarch64"
    ["x86_64-darwin"]="Darwin x86_64"
    ["aarch64-darwin"]="Darwin arm64"
)

# Function to detect current architecture using uname
detect_architecture() {
    local os_name=$(uname -s)
    local arch_name=$(uname -m)
    
    case "$os_name" in
        Linux*)
            case "$arch_name" in
                x86_64) echo "x86_64-linux" ;;
                aarch64|arm64) echo "aarch64-linux" ;;
                *) echo "unsupported" ;;
            esac
            ;;
        Darwin*)
            case "$arch_name" in
                x86_64) echo "x86_64-darwin" ;;
                arm64) echo "aarch64-darwin" ;;
                *) echo "unsupported" ;;
            esac
            ;;
        *)
            echo "unsupported"
            ;;
    esac
}

# Function to validate architecture
validate_architecture() {
    local arch=$1
    if [[ -z "${SUPPORTED_ARCHS[$arch]:-}" ]]; then
        echo -e "${RED}❌ Error: Unsupported architecture '$arch'${NC}"
        echo -e "${YELLOW}Supported architectures:${NC}"
        for supported in "${!SUPPORTED_ARCHS[@]}"; do
            echo -e "  ${BLUE}•${NC} $supported (${SUPPORTED_ARCHS[$supported]})"
        done
        exit 1
    fi
}

# Function to build pytest and show results
build_and_show() {
    local target_arch=$1
    echo -e "${GREEN}🚀 Building pytest check for $target_arch...${NC}"
    
    # Build the pytest check
    if nix build ".#checks.$target_arch.pytest"; then
        echo -e "${GREEN}✅ Build successful!${NC}"
        
        # Check if results exist
        if [[ -d "result" ]]; then
            echo -e "${BLUE}📊 Opening test results in Brave...${NC}"
            brave result/index.html 2>/dev/null || echo -e "${YELLOW}⚠️  Could not open Brave. Results available at: result/index.html${NC}"
        else
            echo -e "${YELLOW}⚠️  No test results found in result/ directory${NC}"
        fi
    else
        echo -e "${RED}❌ Build failed for $target_arch${NC}"
        exit 1
    fi
}

# Main execution
main() {
    local target_arch
    
    if [[ $# -eq 0 ]]; then
        # No arguments provided, detect current architecture
        target_arch=$(detect_architecture)
        if [[ "$target_arch" == "unsupported" ]]; then
            echo -e "${RED}❌ Error: Current system architecture is not supported${NC}"
            echo -e "${YELLOW}Detected: $(uname -s) $(uname -m)${NC}"
            exit 1
        fi
        echo -e "${BLUE}🔍 Detected architecture: $target_arch${NC}"
    else
        # Use provided architecture
        target_arch=$1
    fi
    
    validate_architecture "$target_arch"
    build_and_show "$target_arch"
}

# Run main function with all arguments
main "$@"
