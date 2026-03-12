# 🛡️ R-Defender Packaging Quick Start

## TL;DR - Build Your Installer in 3 Steps

### Step 1: Install Required Tools
```bash
# Install PyInstaller
pip install -r build_requirements.txt

# Download and install NSIS
# https://nsis.sourceforge.io/Download
```

### Step 2: Run the Build Script
**On Windows (easiest):**
```bash
build.bat
```

**On any OS:**
```bash
python build.py
```

### Step 3: Find Your Installer
```
✅ RDefender-Setup.exe  (Ready to distribute!)
```

---

## What Gets Created?

| File | Purpose |
|------|---------|
| `RDefender-Setup.exe` | Windows installer (send this to users) |
| `dist/RDefender/` | Standalone executable folder |
| `dist/RDefender/RDefender.exe` | Main application |

---

## Installation Folder Structure for Users

After installation, users will have:
```
C:\Program Files\RDefender\
├── RDefender.exe          (Launch app here)
├── [all dependencies]
├── [ML models]
├── [config files]
└── Uninstall.exe          (To remove app)
```

---

## What's Included in the Installer?

✅ R-Defender application (Tkinter GUI)  
✅ ML scanning engine (all 4 models + fusion)  
✅ Python runtime (users don't need Python)  
✅ All dependencies (scikit-learn, XGBoost, watchdog, etc.)  
✅ Whitelist database  
✅ Windows registry entries  
✅ Start Menu shortcuts  
✅ Desktop shortcut  
✅ Uninstaller  

---

## File Descriptions

### build_config.spec
PyInstaller configuration file that:
- Specifies which files to bundle
- Includes ML models as data files
- Sets up hidden imports for all dependencies
- Configures the executable output

### installer.nsi
NSIS installer script that:
- Creates the Windows installer wizard
- Handles installation/uninstallation
- Creates shortcuts
- Manages registry entries
- Allows silent installation

### build.py
Automated build script that:
- Checks for required tools
- Cleans old build artifacts
- Runs PyInstaller
- Runs NSIS
- Provides detailed error messages

### build.bat
Windows batch file that:
- Easy double-click building on Windows
- Checks prerequisites
- Calls build.py

---

## File Sizes (Typical)

- RDefender-Setup.exe: 300-400 MB
- Installed size: 600-800 MB (includes Python runtime + models)

The size is large because:
- ML models are large (~200MB total)
- Python runtime is bundled (~100MB)
- scikit-learn + XGBoost: ~200MB
- Unavoidable for standalone apps

---

## Distribution Workflow

1. **Build** → Run build.bat or build.py
2. **Test** → Test RDefender-Setup.exe on a clean Windows VM
3. **Sign** (Optional) → Get code signing certificate for production
4. **Host** → Upload RDefender-Setup.exe to your server/website
5. **Deploy** → Users download and run the installer

---

## Troubleshooting Quick Guide

| Issue | Solution |
|-------|----------|
| "PyInstaller not found" | `pip install pyinstaller --upgrade` |
| "makensis not found" | Install NSIS: https://nsis.sourceforge.io/Download |
| ".joblib files missing" | Verify all model files exist in project root |
| "Build fails silently" | Run `python build.py` for detailed errors |
| Large installer (>500MB) | Normal due to ML models + dependencies |
| Installer won't run on target PC | Ensure target has Windows 7+ and admin rights |

---

## Next Steps

1. Run `python build.py` or `build.bat`
2. Test `RDefender-Setup.exe` on a Windows machine
3. Distribute to users
4. Users will get:
   - Admin installation wizard
   - Desktop/Start Menu shortcuts
   - Full uninstall support via Add/Remove Programs

---

## Advanced Configuration

See **PACKAGING_GUIDE.md** for:
- Custom installation directory
- Application icons
- Silent installation
- Version numbers
- Code signing
- Advanced NSIS customization
