# 🛡️ CREATE INSTALLER NOW - Windows Only

You have: `RDefender.exe`  
You need: `RDefender-Setup.exe`

## ⚡ QUICK FIX (Copy & Paste This)

### On Windows Command Prompt:
```cmd
cd path\to\rdefender_final
makensis installer.nsi
```

### Done! 
Look for: `RDefender-Setup.exe` in the current folder ✅

---

## If That Didn't Work

### Check 1: Is NSIS installed?
```cmd
makensis /version
```
- ✅ Shows version? → Skip to Check 2
- ❌ Command not found? → [Download NSIS](https://nsis.sourceforge.io/Download) and install

### Check 2: Does dist/RDefender/ exist?
```cmd
dir dist\RDefender\RDefender.exe
```
- ✅ File exists? → Run: `makensis installer.nsi`
- ❌ Not found? → Run first: `pyinstaller build_config.spec --clean`

### Check 3: Run the installer build
```cmd
makensis installer.nsi
```

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| "makensis not found" | Install NSIS: https://nsis.sourceforge.io/Download |
| "Unable to find dist/RDefender" | Run: `pyinstaller build_config.spec` first |
| "ERROR in script" | Check all 5 .joblib files exist |
| Nothing happens | Try: `makensis /version` to test NSIS |

---

## You Should Now Have:

```
RDefender-Setup.exe         ← THIS IS WHAT YOU WANT
  (~350 MB, ready to distribute)
```

## What To Do Next:

1. **Test it**: Double-click `RDefender-Setup.exe` to test the installer
2. **Share it**: Upload to your server/website
3. **Users can install**: They run `RDefender-Setup.exe` and follow the wizard

---

## Need More Help?

See: [MANUAL_INSTALLER_CREATION.md](MANUAL_INSTALLER_CREATION.md)
