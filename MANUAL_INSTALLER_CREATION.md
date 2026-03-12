# 🛡️ Manual Windows Installer Creation

## You have: RDefender.exe (the executable)
## You need: RDefender-Setup.exe (the installer)

---

## ✅ SOLUTION: Run NSIS Manually

### On Windows Command Prompt:

```cmd
# Go to your project folder
cd C:\path\to\rdefender_final

# Make sure NSIS is installed and check it works
makensis /version

# Create the installer
makensis installer.nsi
```

### Expected Output:
```
Processing config: installer.nsi
Creating installer
Copying files
Setting permissions
...
Created: RDefender-Setup.exe
```

---

## Alternative: NSIS GUI Method

### Step 1: Open NSIS
- **Windows Start Menu** → Search "NSIS"
- Or go to `C:\Program Files (x86)\NSIS`
- Run `Makensis.exe`

### Step 2: Open Your Script
- Click **File** → **Load Script**
- Select `installer.nsi` from your project folder
- Click **Compile**

### Step 3: Wait for Completion
- Look for: "Created: RDefender-Setup.exe"
- You're done! ✅

---

## Troubleshooting

### "makensis not found"
**Problem:** NSIS not installed or not in PATH

**Solution:**
1. Download NSIS: https://nsis.sourceforge.io/Download
2. Install it (default location is fine)
3. Restart Command Prompt
4. Try again: `makensis /version`

### "Build failed"
**Problem:** NSIS script error

**Solution:**
1. Check the error message carefully
2. Common issues:
   - `dist/RDefender/` folder doesn't exist → Run PyInstaller first
   - File paths are wrong → Check installer.nsi paths
   - Spaces in paths → Use quotes or short names

### "ERROR: Unable to find..."
**Problem:** Missing files referenced in installer.nsi

**Solution:**
1. Verify `dist/RDefender/` exists with all files
2. Run PyInstaller first: `pyinstaller build_config.spec`
3. Check installer.nsi refers to correct paths

---

## Step-by-Step Instructions for Windows

### Step 1: Verify PyInstaller Built Successfully
```cmd
dir dist\RDefender\
# Should show: RDefender.exe and many .pyd/.dll files
```

### Step 2: Verify NSIS is Installed
```cmd
makensis /version
# Should show version number like: v3.08
```

### Step 3: Build the Installer
```cmd
makensis installer.nsi
```

### Step 4: Check Result
```cmd
dir RDefender-Setup.exe
# Should show the file with ~350 MB size
```

### Step 5: Test the Installer
```cmd
RDefender-Setup.exe
# Click through the wizard to verify it works
```

---

## If Automatic Build Script Didn't Work

The `build.py` script might have skipped the NSIS step. Run manually:

```cmd
# Step 1: Build executable (if not done)
pyinstaller build_config.spec --clean

# Step 2: Verify it worked
dir dist\RDefender\RDefender.exe

# Step 3: Build installer
makensis installer.nsi

# Step 4: Verify result
dir RDefender-Setup.exe
```

---

## Python Command Alternative

If you prefer Python:

```python
import subprocess
import os

# Make sure we're in the right directory
os.chdir(r"C:\path\to\rdefender_final")

# Run NSIS
result = subprocess.run(["makensis", "installer.nsi"], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

# Check result
if os.path.exists("RDefender-Setup.exe"):
    print("✅ Installer created successfully!")
    print(f"Size: {os.path.getsize('RDefender-Setup.exe') / (1024*1024):.1f} MB")
else:
    print("❌ Installer creation failed")
```

---

## Once You Have RDefender-Setup.exe

You can:
1. ✅ Test it on another Windows machine
2. ✅ Upload it to your server
3. ✅ Share with users
4. ✅ Users can install with: `RDefender-Setup.exe`

---

## Quick Checklist

- [ ] Copied project to Windows
- [ ] Ran: `pip install -r build_requirements.txt`
- [ ] Ran: `pip install -r requirements.txt`
- [ ] Installed NSIS
- [ ] Ran: `python build.py` OR `pyinstaller build_config.spec && makensis installer.nsi`
- [ ] Verified: `RDefender-Setup.exe` exists
- [ ] File size is ~350 MB
- [ ] Double-clicked installer to test

✅ All done!

---

## Next Steps

1. **Create installer** using steps above
2. **Test the installer** by running it
3. **Distribute RDefender-Setup.exe** to users

That's it! 🎉
