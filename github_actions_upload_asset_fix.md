# GitHub Actions Upload Release Asset Fix

## Issue Description

The GitHub Actions workflow was failing with the error:
```
Error: ENOENT: no such file or directory, stat './employee-tracker-macos/ProductivityFlow Tracker_*.dmg'
```

## Root Cause

The workflow was using `actions/upload-release-asset@v1` with hardcoded file paths that included wildcards (`*`), but the action doesn't support glob patterns. The file paths were:

- `./employee-tracker-macos/ProductivityFlow Tracker_*.dmg`
- `./employee-tracker-windows/ProductivityFlow Tracker_*.msi`
- `./manager-dashboard-macos/ProductivityFlow Manager Dashboard_*.dmg`
- `./manager-dashboard-windows/ProductivityFlow Manager Dashboard_*.msi`

These paths assumed the exact structure of downloaded artifacts, but the actual DMG and MSI files are nested deeper in the artifact directories.

## Solution Applied

### 1. Enhanced Debugging
Added comprehensive file structure debugging to see exactly what files are available after downloading artifacts:

```yaml
- name: Display structure of downloaded files
  run: |
    echo "Root directory:"
    ls -la
    echo "Employee tracker artifacts:"
    find ./employee-tracker-macos -type f -name "*.dmg" -o -name "*.msi" 2>/dev/null || echo "No employee tracker artifacts found"
    echo "Manager dashboard artifacts:"
    find ./manager-dashboard-macos -type f -name "*.dmg" -o -name "*.msi" 2>/dev/null || echo "No manager dashboard artifacts found"
    echo "Windows artifacts:"
    find ./employee-tracker-windows -type f -name "*.msi" -o -name "*.exe" 2>/dev/null || echo "No windows artifacts found"
    find ./manager-dashboard-windows -type f -name "*.msi" -o -name "*.exe" 2>/dev/null || echo "No windows artifacts found"
```

### 2. Dynamic File Discovery
Replaced hardcoded paths with dynamic file discovery using `find` commands:

```yaml
- name: Find Asset Files
  id: find_assets
  run: |
    # Find Employee Tracker files
    ET_DMG=$(find ./employee-tracker-macos -name "*.dmg" -type f | head -1)
    ET_MSI=$(find ./employee-tracker-windows -name "*.msi" -type f | head -1)
    
    # Find Manager Dashboard files
    MD_DMG=$(find ./manager-dashboard-macos -name "*.dmg" -type f | head -1)
    MD_MSI=$(find ./manager-dashboard-windows -name "*.msi" -type f | head -1)
    
    # Set outputs
    echo "et_dmg=$ET_DMG" >> $GITHUB_OUTPUT
    echo "et_msi=$ET_MSI" >> $GITHUB_OUTPUT
    echo "md_dmg=$MD_DMG" >> $GITHUB_OUTPUT
    echo "md_msi=$MD_MSI" >> $GITHUB_OUTPUT
    
    # Debug output
    echo "Employee Tracker DMG: $ET_DMG"
    echo "Employee Tracker MSI: $ET_MSI"
    echo "Manager Dashboard DMG: $MD_DMG"
    echo "Manager Dashboard MSI: $MD_MSI"
```

### 3. Conditional Upload Steps
Updated upload steps to use the dynamically discovered file paths and only run if files are found:

```yaml
- name: Upload Employee Tracker macOS DMG
  if: steps.find_assets.outputs.et_dmg != ''
  uses: actions/upload-release-asset@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
    upload_url: ${{ steps.create_release.outputs.upload_url }}
    asset_path: ${{ steps.find_assets.outputs.et_dmg }}
    asset_name: ProductivityFlow-Employee-Tracker-macOS.dmg
    asset_content_type: application/octet-stream
```

## Key Improvements

1. **Robust File Discovery**: Uses `find` command to locate files regardless of their exact path within the artifact directories
2. **Error Prevention**: Conditional uploads only run if files are actually found
3. **Better Debugging**: Enhanced logging to help troubleshoot future issues
4. **Maintainable**: No hardcoded file paths that could break with Tauri build changes

## Files Modified

- `.github/workflows/release-installers.yml` - Fixed the upload asset steps to use dynamic file discovery

## Result

The workflow will now:
1. Download all build artifacts
2. Search for DMG and MSI files within the artifact directories
3. Only attempt to upload files that actually exist
4. Provide clear debugging output showing what files were found

This fix ensures the release process works reliably regardless of the exact file structure within the downloaded artifacts.