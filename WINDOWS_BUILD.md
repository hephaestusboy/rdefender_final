# 🛡️ R-Defender Windows Build Instructions

Since you're on Linux, use this guide when you get to a Windows machine.

## Prerequisites (One-Time Setup)

### 1. Install Python (if not already installed)
- Download: https://www.python.org/downloads/
- Choose Python 3.8 or later
- ✅ Check "Add Python to PATH" during installation

### 2. Install NSIS (Windows Installer Creator)
- Download: https://nsis.sourceforge.io/Download
- Run the installer
- NSIS will automatically be added to your PATH

### 3. Verify Installations
Open Command Prompt and run:
```cmd
python --version
pyinstaller --version
makensis /version
```

All three should show version numbers without errors.

## Building R-Defender

### Step 1: Copy Project to Windows
Transfer the entire `rdefender_final/` folder to Windows.

Minimum required files:
```
rdefender_final/
├── rdefender_ui_clr_copy.py
├── rdefender_agent.py
├── build_config.spec
├── installer.nsi
├── build.py
├── build_requirements.txt
├── build_requirements.txt
├── [all .joblib model files]
├── [all other Python modules]
└── requirements.txt
```

### Step 2: Install Python Dependencies
Open Command Prompt in the `rdefender_final/` folder:

```cmd
# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r build_requirements.txt
pip install -r requirements.txt
```

### Step 3: Build the Installer

Option A - Automatic (Recommended):
```cmd
python build.py
```

Option B - Manual steps:
```cmd
pyinstaller build_config.spec --clean
makensis installer.nsi
```

### Step 4: Find Your Installer

```
✅ RDefender-Setup.exe
```

This is your final deliverable!

## What Gets Created

| Folder/File | Purpose |
|---|---|
| `build/` | Temporary build files (can delete) |
| `dist/RDefender/` | The executable files |
| `RDefender-Setup.exe` | **Your Windows installer** |

## Distribution

Share `RDefender-Setup.exe` with users. They can:
1. Double-click it
2. Follow the installation wizard
3. Get R-Defender installed in `C:\Program Files\RDefender`

## Installation Size & Time

- **Setup file**: 300-400 MB
- **Installed size**: 600-800 MB
- **Installation time**: 2-5 minutes (depending on disk speed)

## Customization Options

### Change Installation Folder
Edit `installer.nsi` before building:
```nsi
InstallDir "$PROGRAMFILES\RDefender"  # Change this line
```

### Add Custom Icon
1. Create a 256×256 PNG icon
2. Convert to .ico format (use convertio.co or similar)
3. Name it `rdefender_icon.ico`
4. Place in the project root
5. Run `python build.py`

### Change Version Number
Edit `installer.nsi`:
```nsi
WriteRegStr HKLM "..." "DisplayVersion" "1.0"  # Change version here
```

## Troubleshooting

### "Python not found"
- Python not installed, or not in PATH
- Reinstall Python with "Add to PATH" checked

### "PyInstaller not found"
```cmd
pip install pyinstaller --upgrade
```

### "makensis not found"
- NSIS not installed, or not in PATH
- Reinstall NSIS
- Or add NSIS to PATH manually: `C:\Program Files (x86)\NSIS`

### "Missing .joblib files"
Ensure all 5 model files are in the project root:
- `rf_behavior_model.joblib`
- `rf_artifact_model.joblib`
- `xgb_behavior_model.joblib`
- `xgb_artifact_model.joblib`
- `fusion_model.joblib`

### Build takes very long
This is normal! PyInstaller can take 3-10 minutes depending on your PC.
- Don't close the Command Prompt window
- Don't interrupt the process
- Wait for it to complete

### "ERROR: option(s) not allowed" 
If using an old .spec file, remove it:
```cmd
del *.spec
```
(but keep `build_config.spec`)

## Advanced: Silent Installation

Users can install without prompts:
```cmd
RDefender-Setup.exe /S
```

## Advanced: Uninstall
Users can uninstall via:
- Windows Add/Remove Programs
- Command: `C:\Program Files\RDefender\Uninstall.exe /S`

## Building Multiple Versions

If you need to build again after changes:

```cmd
# Clean old builds
rmdir /s build
rmdir /s dist

# Rebuild
python build.py
```

## Support & Issues

If build fails:
1. Check all prerequisites are installed (`python --version`, etc.)
2. Verify all `.joblib` files exist
3. Check that `build_config.spec` hasn't been modified
4. Try manual build: `pyinstaller build_config.spec` then `makensis installer.nsi`
5. Check NSIS compilation log for errors

## Next Steps After Building

1. ✅ Test `RDefender-Setup.exe` on a clean Windows VM
2. ✅ Test installation and functionality
3. ✅ Test uninstallation
4. ✅ Upload to server/website for distribution
5. ✅ Provide download link to users
