# R-Defender Windows Installation Package Guide

## Overview
This guide explains how to package R-Defender into a professional Windows installer (`RDefender-Setup.exe`) that users can install on their systems.

## Prerequisites

### Required Tools
You need to install these tools before building the package:

1. **PyInstaller** (converts Python to .exe)
   ```bash
   pip install pyinstaller
   ```

2. **NSIS** (creates Windows installer)
   - Download from: https://nsis.sourceforge.io/Download
   - Run the installer and complete the installation
   - Make sure NSIS is added to your system PATH

### System Requirements
- Windows 7 or later
- Python 3.8+ (for building)
- ~2GB free disk space (for build artifacts)

## Building the Installer

### Option 1: Automated Build (Recommended)

Run the build script which automates everything:

```bash
python build.py
```

This script will:
1. ✅ Check if required tools are installed
2. 🗑️ Clean old build artifacts
3. 🔧 Build the executable with PyInstaller
4. 📦 Create the Windows installer with NSIS

### Option 2: Manual Build

#### Step 1: Build the Executable
```bash
pyinstaller build_config.spec
```

This creates a `dist/RDefender/` folder with all executable files.

#### Step 2: Build the Installer
```bash
makensis installer.nsi
```

This creates `RDefender-Setup.exe` in the current directory.

## File Structure

```
rdefender_final/
├── build_config.spec          # PyInstaller configuration
├── installer.nsi              # NSIS installer script
├── build.py                   # Automated build script
├── rdefender_ui_clr_copy.py   # Main UI application
├── rdefender_agent.py         # ML scanning engine
├── [model files]              # .joblib files
├── requirements.txt           # Python dependencies
└── dist/
    ├── RDefender/             # Built executable
    └── RDefender-Setup.exe    # Final installer
```

## Output Files

After building:

- **RDefender-Setup.exe** - Windows installer (main deliverable)
- **dist/RDefender/** - Standalone executable folder

## Distributing R-Defender

### User Installation
Users can install R-Defender by:
1. Double-clicking `RDefender-Setup.exe`
2. Following the installation wizard
3. Choosing installation location (default: `C:\Program Files\RDefender`)
4. Creating desktop/start menu shortcuts

### Installation Features
- Start Menu shortcuts
- Desktop shortcut
- Windows Add/Remove Programs entry
- Clean uninstallation

## Customization Options

### Change Installation Directory
Edit `installer.nsi`:
```nsi
InstallDir "$PROGRAMFILES\RDefender"  # Change path here
```

### Add Application Icon
1. Create a 256x256 icon file named `rdefender_icon.ico`
2. Place it in the project root
3. The `build_config.spec` already references it

### Change Installer Name/Version
Edit `installer.nsi`:
```nsi
Name "RDefender"              # Application name
OutFile "RDefender-Setup.exe" # Installer filename
```

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller --upgrade
```

### "makensis not found"
- NSIS is not installed or not in PATH
- Install from: https://nsis.sourceforge.io/Download
- Or add NSIS to your PATH manually

### "Missing model files" error during build
Ensure these files exist in the project root:
- `rf_behavior_model.joblib`
- `rf_artifact_model.joblib`
- `xgb_behavior_model.joblib`
- `xgb_artifact_model.joblib`
- `fusion_model.joblib`

Update `build_config.spec` if model files are in a different location.

### Large installer size (>500MB)
This is normal due to ML models and dependencies. To reduce:
- Compress the .joblib files if possible
- Remove unused dependencies from `hiddenimports`

## Advanced: Silent Installation

Users can install silently (no UI):
```bash
RDefender-Setup.exe /S
```

## Advanced: Uninstallation

Users can uninstall via:
- Add/Remove Programs
- `C:\Program Files\RDefender\Uninstall.exe`
- Command line: `RDefender-Setup.exe /u`

## Package Details

The installer includes:
- ✅ Complete Python runtime
- ✅ All ML models
- ✅ All dependencies (scikit-learn, XGBoost, etc.)
- ✅ Whitelist database
- ✅ Windows registry entries
- ✅ Shortcuts and start menu entries

## Security Notes

- The installer requires **Admin privileges** for system-wide installation
- All dependencies are bundled within the installer
- Users don't need Python installed on their system

## Support

For issues or errors during build:
1. Check that all prerequisites are installed
2. Verify all `.joblib` model files exist
3. Run `python build.py` for detailed error messages
4. Check NSIS logs if installer fails to build
