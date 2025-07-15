#!/bin/bash

set -e

# Create ProductivityFlow Installer App
echo "🔧 Creating ProductivityFlow Installer App..."

INSTALLER_DIR="./ProductivityFlow Installer.app"
CONTENTS_DIR="$INSTALLER_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean and create app structure
rm -rf "$INSTALLER_DIR"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ProductivityFlow Installer</string>
    <key>CFBundleIdentifier</key>
    <string>com.productivityflow.installer</string>
    <key>CFBundleName</key>
    <string>ProductivityFlow Installer</string>
    <key>CFBundleDisplayName</key>
    <string>ProductivityFlow Installer</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleIconFile</key>
    <string>installer-icon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create the main executable script
cat > "$MACOS_DIR/ProductivityFlow Installer" << 'EOF'
#!/bin/bash

# ProductivityFlow Installer
# This installer provides a GUI for selecting which components to install

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"

# Check if we're running from the app bundle
if [[ "$SCRIPT_DIR" == *".app/Contents/MacOS" ]]; then
    # Running from app bundle
    cd "$RESOURCES_DIR"
else
    # Running from development
    cd "$(dirname "$0")"
fi

# Launch the installer GUI
python3 installer_gui.py
EOF

# Make the executable script executable
chmod +x "$MACOS_DIR/ProductivityFlow Installer"

# Create the Python GUI installer
cat > "$RESOURCES_DIR/installer_gui.py" << 'EOF'
#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import subprocess
import sys
from pathlib import Path

class ProductivityFlowInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ProductivityFlow Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variables for checkboxes
        self.install_tracker = tk.BooleanVar(value=True)
        self.install_manager = tk.BooleanVar(value=True)
        
        # Get the applications directory
        self.applications_dir = "/Applications"
        
        # Get the current directory (should be Resources)
        self.installer_dir = Path(__file__).parent
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="ProductivityFlow Suite", 
                               font=("Helvetica", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Choose which components you want to install:", 
                                  font=("Helvetica", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Employee Tracker checkbox
        tracker_frame = ttk.Frame(main_frame)
        tracker_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(tracker_frame, text="Install Employee Tracker", 
                       variable=self.install_tracker).grid(row=0, column=0, sticky=tk.W)
        
        tracker_desc = ttk.Label(tracker_frame, 
                                text="Track employee productivity and time management",
                                font=("Helvetica", 10), foreground="gray")
        tracker_desc.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        
        # Manager Dashboard checkbox
        manager_frame = ttk.Frame(main_frame)
        manager_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(manager_frame, text="Install Manager Dashboard", 
                       variable=self.install_manager).grid(row=0, column=0, sticky=tk.W)
        
        manager_desc = ttk.Label(manager_frame, 
                                text="Comprehensive dashboard for managers to monitor team productivity",
                                font=("Helvetica", 10), foreground="gray")
        manager_desc.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        
        # Installation path
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(30, 20))
        
        ttk.Label(path_frame, text="Installation Path:", 
                 font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(path_frame, text=self.applications_dir, 
                 font=("Helvetica", 11)).grid(row=1, column=0, sticky=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Install button
        install_btn = ttk.Button(buttons_frame, text="Install Selected Components", 
                               command=self.install_components, 
                               style="Accent.TButton")
        install_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", 
                              command=self.root.quit)
        cancel_btn.grid(row=0, column=1)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100)
        
        # Status label (initially hidden)
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def show_progress(self):
        """Show progress bar and status label"""
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 5))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update()
        
    def install_components(self):
        """Install selected components"""
        if not self.install_tracker.get() and not self.install_manager.get():
            messagebox.showwarning("No Selection", 
                                 "Please select at least one component to install.")
            return
        
        # Show progress
        self.show_progress()
        
        try:
            total_steps = 0
            if self.install_tracker.get():
                total_steps += 1
            if self.install_manager.get():
                total_steps += 1
            
            current_step = 0
            
            # Install Employee Tracker
            if self.install_tracker.get():
                current_step += 1
                self.update_progress((current_step / total_steps) * 50, 
                                   "Installing Employee Tracker...")
                self.install_app("ProductivityFlow Tracker.app")
                self.update_progress((current_step / total_steps) * 100, 
                                   "Employee Tracker installed successfully")
            
            # Install Manager Dashboard
            if self.install_manager.get():
                current_step += 1
                self.update_progress((current_step / total_steps) * 50 + 50, 
                                   "Installing Manager Dashboard...")
                self.install_app("ProductivityFlow Manager Dashboard.app")
                self.update_progress(100, "Manager Dashboard installed successfully")
            
            # Success message
            messagebox.showinfo("Installation Complete", 
                              "ProductivityFlow components have been installed successfully!")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Installation Error", 
                               f"An error occurred during installation: {str(e)}")
    
    def install_app(self, app_name):
        """Install a single app to Applications folder"""
        app_path = self.installer_dir / app_name
        target_path = Path(self.applications_dir) / app_name
        
        if not app_path.exists():
            raise Exception(f"Application not found: {app_name}")
        
        # Remove existing installation if it exists
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # Copy the app
        shutil.copytree(app_path, target_path)
        
        # Make executable
        executable_path = target_path / "Contents" / "MacOS"
        if executable_path.exists():
            for file in executable_path.iterdir():
                if file.is_file():
                    file.chmod(0o755)
    
    def run(self):
        """Run the installer"""
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

if __name__ == "__main__":
    installer = ProductivityFlowInstaller()
    installer.run()
EOF

# Make Python script executable
chmod +x "$RESOURCES_DIR/installer_gui.py"

echo "✅ ProductivityFlow Installer App created successfully!"