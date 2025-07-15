#!/bin/bash

set -e

# ProductivityFlow Unified Installer Build Script
echo "🚀 Building ProductivityFlow Unified Installer..."

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
    
    # Check if create-dmg is installed, if not install it
    if ! command -v create-dmg &> /dev/null; then
        print_warning "create-dmg not found. Installing..."
        if command -v brew &> /dev/null; then
            brew install create-dmg
        else
            print_error "Homebrew is required to install create-dmg"
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

# Create installer structure
create_installer_structure() {
    print_status "Creating installer structure..."
    
    # Clean and create temp directory
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    # Copy built applications
    print_status "Copying built applications..."
    
    # Find and copy Employee Tracker .app
    EMPLOYEE_TRACKER_APP=$(find employee-tracker-tauri/src-tauri/target -name "*.app" -type d | head -1)
    if [ -z "$EMPLOYEE_TRACKER_APP" ]; then
        print_error "Employee Tracker .app not found"
        exit 1
    fi
    cp -R "$EMPLOYEE_TRACKER_APP" "$TEMP_DIR/"
    
    # Find and copy Manager Dashboard .app
    MANAGER_DASHBOARD_APP=$(find manager-dashboard-tauri/src-tauri/target -name "*.app" -type d | head -1)
    if [ -z "$MANAGER_DASHBOARD_APP" ]; then
        print_error "Manager Dashboard .app not found"
        exit 1
    fi
    cp -R "$MANAGER_DASHBOARD_APP" "$TEMP_DIR/"
    
    # Copy installer files
    cp -R installer/* "$TEMP_DIR/"
    
    print_success "Installer structure created."
}

# Create the unified DMG
create_dmg() {
    print_status "Creating unified .dmg installer..."
    
    DMG_NAME="${INSTALLER_NAME}.dmg"
    
    # Remove existing DMG
    rm -f "$OUTPUT_DIR/$DMG_NAME"
    
    # Create the DMG with custom installer
    create-dmg \
        --volname "ProductivityFlow Installer" \
        --volicon "installer/assets/volume-icon.icns" \
        --background "installer/assets/background.png" \
        --window-pos 200 120 \
        --window-size 800 600 \
        --icon-size 100 \
        --icon "ProductivityFlow Installer.app" 200 300 \
        --hide-extension "ProductivityFlow Installer.app" \
        --app-drop-link 600 300 \
        "$OUTPUT_DIR/$DMG_NAME" \
        "$TEMP_DIR"
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    
    print_success "Unified .dmg installer created: $OUTPUT_DIR/$DMG_NAME"
}

# Main execution
main() {
    print_status "Starting ProductivityFlow Unified Installer build process..."
    
    check_dependencies
    build_employee_tracker
    build_manager_dashboard
    create_installer_structure
    create_dmg
    
    print_success "✨ ProductivityFlow Unified Installer build completed!"
    print_status "Installer location: $OUTPUT_DIR/${INSTALLER_NAME}.dmg"
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi