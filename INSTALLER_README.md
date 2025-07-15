# ProductivityFlow Unified Installer

This project provides a sophisticated unified installer for the ProductivityFlow application suite on macOS. The installer creates a single .dmg file that contains a custom installer application with a graphical interface for selecting which components to install.

## 🎯 Features

- **Unified Installer**: Single .dmg file for both applications
- **Custom GUI**: Professional installer interface with checkboxes
- **Selective Installation**: Users can choose which components to install
- **Progress Tracking**: Real-time installation progress with status updates
- **Professional Branding**: Custom background and icons for ProductivityFlow
- **Error Handling**: Comprehensive error handling and user feedback

## 📦 What Gets Installed

The installer can install two applications:

1. **ProductivityFlow Tracker** (`com.productivityflow.tracker`)
   - Employee productivity tracking application
   - Compact interface (400x600 pixels)

2. **ProductivityFlow Manager Dashboard** (`com.productivityflow.manager`)
   - Manager dashboard for monitoring team productivity
   - Full-featured interface (1200x800 pixels)

## 🛠 Prerequisites

Before building the installer, ensure you have:

- **macOS** (required for .dmg creation)
- **Node.js & npm** (for building Tauri applications)
- **Rust & Cargo** (for Tauri applications)
- **Python 3** (for installer GUI)
- **Homebrew** (for installing create-dmg)

Optional for enhanced assets:
- **Pillow (PIL)** for generating custom icons and backgrounds:
  ```bash
  pip3 install Pillow
  ```

## 🚀 Quick Start

### Option 1: Build Everything (Recommended)

```bash
# Make the script executable
chmod +x build-unified-installer.sh

# Build the complete installer
./build-unified-installer.sh

# Or build and test immediately
./build-unified-installer.sh --test
```

### Option 2: Manual Build Steps

```bash
# 1. Build individual applications
cd employee-tracker-tauri && npm install && npm run tauri build && cd ..
cd manager-dashboard-tauri && npm install && npm run tauri build && cd ..

# 2. Create installer assets
cd installer/assets
chmod +x create-placeholder-assets.sh
./create-placeholder-assets.sh
cd ../..

# 3. Create installer app
cd installer/scripts
chmod +x create-installer-app.sh
./create-installer-app.sh
cd ../..

# 4. Package everything
./build-unified-installer.sh
```

## 📁 Project Structure

```
├── employee-tracker-tauri/          # Employee tracker Tauri app
├── manager-dashboard-tauri/         # Manager dashboard Tauri app
├── installer/                       # Installer infrastructure
│   ├── assets/                      # Icons, backgrounds, etc.
│   │   └── create-placeholder-assets.sh
│   ├── scripts/                     # Installer app creation
│   │   └── create-installer-app.sh
│   └── templates/                   # Template files
├── build-installer.sh               # Original build script
├── build-unified-installer.sh       # Enhanced build script
└── dist/                           # Output directory
    └── ProductivityFlow-Installer.dmg
```

## 🎨 Customizing the Installer

### Custom Branding

Replace the placeholder assets in `installer/assets/`:

- **background.png**: DMG background image (800x600 recommended)
- **installer-icon.icns**: Installer app icon (512x512 base size)
- **volume-icon.icns**: DMG volume icon

### Custom Installer UI

The installer GUI is built with Python tkinter and can be customized by modifying the `installer_gui.py` file created by the build process. You can:

- Change colors and fonts
- Modify the layout
- Add additional information or branding
- Customize the installation logic

### Example: Custom Colors

Edit the `installer_gui.py` file and modify:

```python
# Change the background color
image = Image.new('RGBA', (size, size), color=(YOUR_R, YOUR_G, YOUR_B, 255))

# Update the title styling
title_label = ttk.Label(main_frame, text="Your App Suite", 
                       font=("Your Font", 24, "bold"))
```

## 🔧 Build Configuration

### Environment Variables

You can customize the build process using environment variables:

```bash
# Custom output directory
OUTPUT_DIR="./custom-dist" ./build-unified-installer.sh

# Custom installer name
INSTALLER_NAME="MyApp-Installer" ./build-unified-installer.sh
```

### Build Options

```bash
# Show help
./build-unified-installer.sh --help

# Build and test immediately
./build-unified-installer.sh --test
```

## 🧪 Testing the Installer

### Manual Testing

1. **Build the installer**:
   ```bash
   ./build-unified-installer.sh --test
   ```

2. **Mount the DMG**: The script will automatically open the .dmg file

3. **Run the installer**: Double-click "ProductivityFlow Installer.app"

4. **Test the interface**:
   - Check/uncheck components
   - Verify the installation process
   - Confirm apps appear in /Applications

### Automated Testing

```bash
# Test just the installer app creation
cd installer/scripts
./create-installer-app.sh
open "ProductivityFlow Installer.app"
```

## 📋 User Experience

When users download and open your .dmg file:

1. **Mount DMG**: User double-clicks the .dmg file
2. **Launch Installer**: User double-clicks the installer app
3. **Select Components**: Professional GUI with checkboxes appears
4. **Choose Installation**: User selects desired components
5. **Install**: Click "Install Selected Components"
6. **Progress Tracking**: Real-time progress with status updates
7. **Completion**: Success message and automatic cleanup

## 🔍 Troubleshooting

### Common Issues

**Build fails - missing dependencies**:
```bash
# Install missing tools
brew install create-dmg
pip3 install Pillow
```

**Tauri build fails**:
```bash
# Clean and rebuild
cd employee-tracker-tauri
rm -rf node_modules target
npm install
npm run tauri build
```

**Python GUI doesn't work**:
```bash
# Check Python tkinter
python3 -c "import tkinter; print('tkinter available')"

# Install tkinter on Linux (if needed)
sudo apt-get install python3-tk
```

**DMG creation fails**:
```bash
# Install create-dmg
brew install create-dmg

# Check permissions
chmod +x build-unified-installer.sh
```

### Debug Mode

Enable verbose output:

```bash
# Add debug flag to script
set -x  # Add this line to build-unified-installer.sh
```

## 🔐 Code Signing (Production)

For production deployment, you'll want to sign your applications:

```bash
# Sign the individual apps
codesign --force --deep --sign "Developer ID Application: Your Name" "path/to/app.app"

# Sign the installer
codesign --force --deep --sign "Developer ID Application: Your Name" "ProductivityFlow Installer.app"

# Notarize (if distributing outside App Store)
xcrun notarytool submit "ProductivityFlow-Installer.dmg" --keychain-profile "AC_PASSWORD" --wait
```

## 📄 License & Credits

This installer system uses:
- **create-dmg**: For DMG creation
- **Python tkinter**: For GUI interface
- **Tauri**: For the applications being packaged

## 🤝 Contributing

To improve the installer system:

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the build logs for error messages
3. Ensure all prerequisites are installed
4. Test on a clean macOS system

---

**Happy Installing! 🎉**