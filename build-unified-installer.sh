#!/bin/bash

set -e

# ProductivityFlow Unified Installer Build Script (Enhanced)
echo "🚀 Building ProductivityFlow Unified Installer with Custom UI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALLER_NAME="ProductivityFlow-Installer"
OUTPUT_DIR="./dist"
TEMP_DIR="./temp-installer"
INSTALLER_APP_NAME="ProductivityFlow Installer.app"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed."
        exit 1
    fi
    
    # Check if cargo is installed
    if ! command -v cargo &> /dev/null; then
        print_error "cargo is required but not installed."
        exit 1
    fi
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "python3 is required for the installer GUI."
        exit 1
    fi
    
    # Check if create-dmg is installed, if not install it
    if ! command -v create-dmg &> /dev/null; then
        print_warning "create-dmg not found. Installing..."
        if command -v brew &> /dev/null; then
            brew install create-dmg
        else
            print_error "Homebrew is required to install create-dmg"
            print_status "Install Homebrew from https://brew.sh/ and try again"
            exit 1
        fi
    fi
    
    print_success "All dependencies are available."
}

# Build Employee Tracker
build_employee_tracker() {
    print_status "Building Employee Tracker..."
    cd employee-tracker-tauri
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing Employee Tracker dependencies..."
        npm install
    fi
    
    # Build the application
    print_status "Building Employee Tracker Tauri app..."
    npm run tauri build
    
    cd ..
    print_success "Employee Tracker built successfully."
}

# Build Manager Dashboard
build_manager_dashboard() {
    print_status "Building Manager Dashboard..."
    cd manager-dashboard-tauri
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing Manager Dashboard dependencies..."
        npm install
    fi
    
    # Build the application
    print_status "Building Manager Dashboard Tauri app..."
    npm run tauri build
    
    cd ..
    print_success "Manager Dashboard built successfully."
}

# Create installer assets
create_installer_assets() {
    print_status "Creating installer assets..."
    
    cd installer/assets
    chmod +x create-placeholder-assets.sh
    ./create-placeholder-assets.sh
    cd ../..
    
    print_success "Installer assets created."
}

# Create the custom installer app
create_installer_app() {
    print_status "Creating custom installer app..."
    
    cd installer/scripts
    chmod +x create-installer-app.sh
    ./create-installer-app.sh
    cd ../..
    
    print_success "Custom installer app created."
}

# Create installer structure
create_installer_structure() {
    print_status "Creating installer structure..."
    
    # Clean and create temp directory
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    # Copy the installer app
    print_status "Copying installer app..."
    cp -R "installer/scripts/$INSTALLER_APP_NAME" "$TEMP_DIR/"
    
    # Copy built applications to installer app's Resources directory
    print_status "Copying built applications..."
    
    INSTALLER_RESOURCES="$TEMP_DIR/$INSTALLER_APP_NAME/Contents/Resources"
    
    # Find and copy Employee Tracker .app
    EMPLOYEE_TRACKER_APP=$(find employee-tracker-tauri/src-tauri/target -name "*.app" -type d | head -1)
    if [ -z "$EMPLOYEE_TRACKER_APP" ]; then
        print_error "Employee Tracker .app not found"
        print_status "Make sure the Employee Tracker has been built successfully"
        exit 1
    fi
    cp -R "$EMPLOYEE_TRACKER_APP" "$INSTALLER_RESOURCES/"
    print_status "Copied: $(basename "$EMPLOYEE_TRACKER_APP")"
    
    # Find and copy Manager Dashboard .app
    MANAGER_DASHBOARD_APP=$(find manager-dashboard-tauri/src-tauri/target -name "*.app" -type d | head -1)
    if [ -z "$MANAGER_DASHBOARD_APP" ]; then
        print_error "Manager Dashboard .app not found"
        print_status "Make sure the Manager Dashboard has been built successfully"
        exit 1
    fi
    cp -R "$MANAGER_DASHBOARD_APP" "$INSTALLER_RESOURCES/"
    print_status "Copied: $(basename "$MANAGER_DASHBOARD_APP")"
    
    # Copy installer assets
    cp installer/assets/*.icns "$INSTALLER_RESOURCES/" 2>/dev/null || true
    cp installer/assets/*.png "$INSTALLER_RESOURCES/" 2>/dev/null || true
    
    print_success "Installer structure created."
}

# Create the unified DMG
create_dmg() {
    print_status "Creating unified .dmg installer..."
    
    DMG_NAME="${INSTALLER_NAME}.dmg"
    
    # Remove existing DMG
    rm -f "$OUTPUT_DIR/$DMG_NAME"
    
    # Check if we have background and volume icon
    BACKGROUND_ARG=""
    VOLUME_ICON_ARG=""
    
    if [ -f "installer/assets/background.png" ]; then
        BACKGROUND_ARG="--background installer/assets/background.png"
    fi
    
    if [ -f "installer/assets/volume-icon.icns" ]; then
        VOLUME_ICON_ARG="--volicon installer/assets/volume-icon.icns"
    fi
    
    # Create the DMG with custom installer
    create-dmg \
        --volname "ProductivityFlow Installer" \
        $VOLUME_ICON_ARG \
        $BACKGROUND_ARG \
        --window-pos 200 120 \
        --window-size 800 600 \
        --icon-size 100 \
        --icon "$INSTALLER_APP_NAME" 400 300 \
        --hide-extension "$INSTALLER_APP_NAME" \
        "$OUTPUT_DIR/$DMG_NAME" \
        "$TEMP_DIR"
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    
    print_success "Unified .dmg installer created: $OUTPUT_DIR/$DMG_NAME"
}

# Test the installer (optional)
test_installer() {
    if [ "$1" = "--test" ]; then
        print_status "Testing the installer..."
        if [ -f "$OUTPUT_DIR/${INSTALLER_NAME}.dmg" ]; then
            print_status "Opening the installer for testing..."
            open "$OUTPUT_DIR/${INSTALLER_NAME}.dmg"
        else
            print_error "Installer not found for testing"
        fi
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --test        Open the installer after building (for testing)"
    echo "  --help        Show this help message"
    echo ""
    echo "This script will:"
    echo "1. Check dependencies"
    echo "2. Build both Tauri applications"
    echo "3. Create installer assets"
    echo "4. Create the custom installer app"
    echo "5. Package everything into a unified .dmg"
    echo ""
}

# Main execution
main() {
    # Parse arguments
    if [[ "$1" = "--help" ]]; then
        show_usage
        exit 0
    fi
    
    print_status "Starting ProductivityFlow Unified Installer build process..."
    
    check_dependencies
    build_employee_tracker
    build_manager_dashboard
    create_installer_assets
    create_installer_app
    create_installer_structure
    create_dmg
    test_installer "$1"
    
    print_success "✨ ProductivityFlow Unified Installer build completed!"
    print_status "📦 Installer location: $OUTPUT_DIR/${INSTALLER_NAME}.dmg"
    echo ""
    print_status "🎯 What happens when users open the .dmg:"
    print_status "   1. They see a custom installer window"
    print_status "   2. They can choose which components to install"
    print_status "   3. Selected apps are installed to /Applications"
    echo ""
    print_status "💡 To test the installer, run: $0 --test"
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi