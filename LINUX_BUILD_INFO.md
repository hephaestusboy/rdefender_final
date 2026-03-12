# R-Defender Linux Build Instructions

You're on Linux, which is great for development! However, to create the final Windows installer, you'll need Windows with NSIS.

## Quick Option: Use Pre-Built Binary (Recommended)

If you want to skip the long build process:

1. **Get a pre-built executable** from the project releases, OR
2. **Copy this folder to Windows** and follow the Windows build instructions

## Full Build Process

### Step 1: Build Executable on Linux (Optional)
```bash
source virtual/bin/activate
pyinstaller build_config.spec --clean
```

This creates `dist/RDefender/` (you can skip this - see Step 2 instead)

### Step 2: Create Windows Installer on Windows Machine

#### Option A: Transfer Built Executable
1. Copy `dist/RDefender/` to Windows
2. Copy `installer.nsi` to Windows  
3. Follow Windows build instructions (see WINDOWS_BUILD.md)

#### Option B: Full Build on Windows
1. Transfer entire project to Windows
2. On Windows:
   ```bash
   pip install -r build_requirements.txt
   # Download and install NSIS from https://nsis.sourceforge.io/Download
   python build.py
   ```
3. Get `RDefender-Setup.exe`

## Alternative: Use Docker

If you want to build on Linux without Windows, you can use Docker:

```bash
# Build Linux version
pyinstaller build_config.spec

# Or build for Windows using Wine (advanced)
# This requires wine and 32-bit support - not recommended
```

## What You Need for Windows Build

- **Windows 7+** (or Windows VM)
- **Python 3.8+**
- **NSIS** (https://nsis.sourceforge.io/Download)
- **PyInstaller** (pip install pyinstaller)

## TL;DR

For the fastest path to a Windows installer:

1. **On this Linux machine:** 
   ```
   (Just copy the project folder to Windows)
   ```

2. **On Windows:**
   ```
   pip install -r build_requirements.txt
   # Install NSIS 
   python build.py
   ```

3. **Result:** `RDefender-Setup.exe` ready to distribute!

---

**Why the two-step process?**

- NSIS is Windows-only (can't run on Linux)
- PyInstaller works on Linux but creates Linux binaries
- For Windows binaries, we need to build on Windows or use advanced cross-compilation

**Time estimates:**

- Full build on Linux: 5-10 minutes
- PyInstaller alone: 3-5 minutes  
- NSIS on Windows: < 1 minute
- Total time if doing on Linux then Windows: ~10 minutes
