# 🛡️ Fix FileNotFoundError: mscerts

## Problem
```
FileNotFoundError: \\mscerts\\authroot.stl
```

The `mscerts` certificate data files aren't bundled with the executable.

---

## ✅ Solution (3 Steps)

### Step 1: Update build_config.spec

On Windows, edit your `build_config.spec` file:

**Find this line in the `hiddenimports` list:**
```python
hiddenimports=[
    'sklearn',
    'sklearn.ensemble',
    'sklearn.tree',
    'xgboost',
    'joblib',
    'numpy',
    'watchdog',
    'psutil',
],
```

**Change it to:**
```python
hiddenimports=[
    'sklearn',
    'sklearn.ensemble',
    'sklearn.tree',
    'xgboost',
    'joblib',
    'numpy',
    'watchdog',
    'psutil',
    'mscerts',  # ← ADD THIS LINE
],
```

### Step 2: Rebuild Everything

On Windows Command Prompt:
```cmd
# Clean old builds
rmdir /s build
rmdir /s dist

# Rebuild executable
pyinstaller build_config.spec --clean

# Create installer
makensis installer.nsi
```

### Step 3: Test the New Installer

```cmd
# Uninstall the old version (Add/Remove Programs)
# Then run the new installer
RDefender-Setup.exe
```

---

## Why This Works

- `mscerts` is a hidden import (PyInstaller doesn't detect it automatically)
- Adding to `hiddenimports` tells PyInstaller to include it
- This ensures the certificate files are bundled

---

## Alternative: Manual Bundle

If the above doesn't work, you can manually add the mscerts folder:

**In build_config.spec, find the `datas` list:**
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
],
```

**Change it to:**
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
    # Find mscerts in your Python installation and add it:
    # For example: from venv\Lib\site-packages
],
```

---

## Quick Checklist

- [ ] Edited build_config.spec (added 'mscerts' to hiddenimports)
- [ ] Cleaned build folder: `rmdir /s build dist`
- [ ] Rebuilt: `pyinstaller build_config.spec --clean`
- [ ] Created installer: `makensis installer.nsi`
- [ ] Uninstalled old version
- [ ] Installed new RDefender-Setup.exe
- [ ] Tested - no more FileNotFoundError ✅

---

## If Still Not Working

Try this diagnostic:

```cmd
# Check if mscerts is in your Python
python -c "import mscerts; print(mscerts.__file__)"

# If it works, mscerts is installed
# If it fails, install it:
pip install mscerts
```

Then rebuild.

---

## What Gets Fixed

After rebuilding:
- ✅ All certificate data included
- ✅ No more mscerts errors
- ✅ Program runs successfully
- ✅ All dependencies bundled

---

## Download Fixed Spec (Optional)

If you don't want to edit manually, download the fixed version from the Linux machine:
- File: `build_config_FIXED.spec`
- Copy it as `build_config.spec`
- Then rebuild

---

That's it! The new installer will include all missing files. 🎉
