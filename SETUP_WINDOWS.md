# 🛡️ R-Defender - Windows Setup & Build Guide

Complete guide for setting up and building R-Defender on Windows.

## Table of Contents
1. [Installation (Pre-Built)](#installation-pre-built)
2. [Development Setup](#development-setup)
3. [Building from Source](#building-from-source)
4. [Troubleshooting](#troubleshooting)

---

## Installation (Pre-Built)

### For End Users
If you have `RDefender-Setup.exe`:

1. **Download** the installer
2. **Run** `RDefender-Setup.exe`
3. **Follow** the installation wizard
4. **Launch** from Start Menu or Desktop shortcut

**Installation Location**: `C:\Program Files\RDefender\`

**System Requirements**:
- Windows 10 or later
- 4GB RAM minimum
- 500MB disk space
- Internet (optional, for updates)

---

## Development Setup

### Prerequisites

#### Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Download Python 3.8 or later (3.10+ recommended)
3. **Important**: Check ✅ "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   ```

#### Step 2: Install NSIS (Windows Installer Builder)
1. Go to https://nsis.sourceforge.io/Download
2. Download the installer
3. Run NSIS installer (default settings are fine)
4. Verify installation:
   ```cmd
   makensis /version
   ```

#### Step 3: Clone/Download Project
```cmd
# Option 1: Clone if you have Git
git clone <repo-url>

# Option 2: Download ZIP and extract
# Then navigate to the folder
cd C:\path\to\rdefender_final
```

### Create Virtual Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
```

### Install Dependencies

```cmd
# Install runtime dependencies
pip install -r requirements.txt

# Install build dependencies
pip install -r build_requirements.txt
```

**Expected output**: All packages installed successfully

---

## Building from Source

### Quick Build (Recommended)

```cmd
# Ensure venv is activated
.\venv\Scripts\activate

# Run the build script
python build.py
```

**Output**: `RDefender-Setup.exe` (ready to distribute)

### Step-by-Step Manual Build

#### Step 1: Clean Previous Builds
```cmd
# Remove old build artifacts
rmdir /s /q build dist
```

#### Step 2: Build Executable with PyInstaller
```cmd
.\venv\Scripts\activate
python -m PyInstaller build_config.spec --clean
```

**Output**: `dist/RDefender/RDefender.exe` (executable folder)

#### Step 3: Create Windows Installer with NSIS
```cmd
makensis installer.nsi
```

**Output**: `RDefender-Setup.exe`

#### Step 4: Test Installer
1. Run `RDefender-Setup.exe`
2. Follow installation wizard
3. Launch application from Start Menu
4. Enable monitoring and verify it works

---

## Build Configuration

### Understanding build_config.spec

Key sections:
```python
# Data files to bundle
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    # ... other ML models ...
    (r'C:\path\to\xgboost', 'xgboost'),  # XGBoost library
    (r'C:\path\to\mscerts', 'mscerts'),  # Certificate validation
]

# Hidden imports for dependencies
hiddenimports=[
    'sklearn',
    'sklearn.ensemble',
    'sklearn.tree',
    'xgboost',
    # ... more modules ...
]
```

### File Requirements

Ensure these files exist before building:
- `rdefender_ui_clr_copy.py` - Main UI
- `rdefender_agent.py` - ML engine
- `static_feature_extractor.py` - Feature extraction
- All `.joblib` files (5 models)
- `*.nsi` files (installer script)

---

## Troubleshooting

### Python Not Found
```cmd
# Error: 'python' is not recognized

# Solution 1: Python not in PATH
# Reinstall Python and check "Add Python to PATH"

# Solution 2: Use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe build.py
```

### PyInstaller Not Found
```cmd
# Error: No module named pyinstaller

# Solution:
pip install pyinstaller>=6.0.0
```

### NSIS Not Found
```cmd
# Error: makensis is not recognized

# Solution 1: Ensure NSIS is installed
# Download from https://nsis.sourceforge.io/Download

# Solution 2: Add to PATH manually
# C:\Program Files (x86)\NSIS
```

### XGBoost Library Missing Error
```
XGBoostLibraryNotFound: Cannot find XGBoost Library in the candidate path
```

**Solution**:
1. Activate venv: `.\venv\Scripts\activate`
2. Install xgboost: `pip install xgboost`
3. Rebuild: `python build.py`

### mscerts Error
```
FileNotFoundError: Cannot find mscerts library
```

**Solution**:
1. Install mscerts: `pip install mscerts`
2. Verify in build_config.spec the path is correct
3. Rebuild: `python build.py`

### sklearn.calibration ModuleNotFoundError
```
ModuleNotFoundError: No module named 'sklearn.calibration'
```

**Solution**:
1. Reinstall scikit-learn: `pip install --upgrade scikit-learn`
2. Rebuild: `python build.py`

### Build Takes Too Long
```
# First build takes 2-5 minutes (normal)
# Subsequent builds faster due to caching

# To force clean rebuild (slower but thorough):
python build.py
# Will automatically clean before building
```

### Installer Won't Create
```
# Ensure all files are present:
- installer.nsi exists
- dist/RDefender/ folder exists
- All dependencies are bundled

# Run with verbose output:
makensis /V4 installer.nsi
```

### Installation Fails
1. **Check**: Disk space (at least 500MB free)
2. **Check**: User has admin rights
3. **Check**: Antivirus isn't blocking installer
4. **Try**: Disable antivirus temporarily during install

### Application Won't Launch
1. Check `rdefender_events.log` for errors
2. Verify all model files exist
3. Check Event Viewer for system errors
4. Try reinstalling

### Monitoring Not Working
1. Ensure you have admin rights
2. Check Windows file system permissions
3. Verify watch directory is accessible
4. Check antivirus isn't blocking file system monitoring

---

## Advanced Configuration

### Change Watch Directory

Edit `rdefender_agent.py`:
```python
TARGET_WATCH_DIR = "C:\\"  # Change this path
```

### Adjust Detection Thresholds

Edit `rdefender_agent.py`:
```python
MALWARE_THRESHOLD = 0.65       # Lower = more sensitive
SUSPICIOUS_THRESHOLD = 0.30    # Lower = more sensitivity
```

### Custom Installer Settings

Edit `installer.nsi`:
```nsis
!define APP_NAME "R-Defender"
!define PRODUCT_VERSION "1.0.0"
!define INSTALL_DIR "$PROGRAMFILES\RDefender"
```

---

## Distribution

### Creating Portable Version

```cmd
# After building with PyInstaller
# Copy the dist/RDefender/ folder
# Users can run RDefender.exe directly without installing

# For easy distribution:
# Zip the dist/RDefender/ folder
# Users extract and run
```

### Using Setup.exe

1. **For Deployment**: Distribute `RDefender-Setup.exe`
2. **Silent Installation**: 
   ```cmd
   RDefender-Setup.exe /S
   ```
3. **For IT**: Create deployment package with installer

---

## Performance Tips

- First run initializes ML models (~5 seconds)
- Subsequent runs faster
- Monitor CPU usage with Task Manager
- Quarantine cleanup manually (Settings button)

---

## Security Notes

- Application requires admin rights for monitoring
- Models are included in executable (not downloaded)
- Whitelist stored locally in `rdefender_whitelist.json`
- Quarantine stored in `C:\RDefender_Quarantine\`
- All operations are logged in `rdefender_events.log`

---

## Support

For issues:
1. Check this troubleshooting section
2. Review log file: `rdefender_events.log`
3. Verify system requirements
4. Try clean reinstall

---

## Next Steps

- See [README.md](README.md) for feature overview
- See [SETUP_LINUX.md](SETUP_LINUX.md) for Linux guide
- Check `requirements.txt` for dependency versions
