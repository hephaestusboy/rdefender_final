# 🛡️ Quick Diagnostic for mscerts Issue

Run this on Windows Command Prompt to diagnose:

## Step 1: Check if mscerts is installed
```cmd
python -c "import mscerts; print('✅ mscerts found at:', mscerts.__file__)"
```

Expected output:
```
✅ mscerts found at: C:\...\site-packages\mscerts\__init__.py
```

---

## Step 2: Find the data file location
```cmd
python -c "import mscerts, os; path = os.path.dirname(mscerts.__file__); print('mscerts folder:', path); import glob; files = glob.glob(os.path.join(path, '*.stl')); print('Certificate files:', files)"
```

Expected output:
```
mscerts folder: C:\Users\...\site-packages\mscerts
Certificate files: ['C:\...\mscerts\authroot.stl', ...]
```

**Copy the mscerts folder path** (first path shown) - you'll use this in the next step.

---

## Step 3: Create a Python script to fix build_config.spec

Save this as `fix_mscerts.py`:

```python
import os
import mscerts

# Find mscerts location
mscerts_path = os.path.dirname(mscerts.__file__)
print(f"Found mscerts at: {mscerts_path}")

# Read build_config.spec
with open('build_config.spec', 'r') as f:
    content = f.read()

# Check if already has mscerts in datas
if "('mscerts'" not in content or mscerts_path not in content:
    # Find the datas section and add mscerts
    old_datas = """datas=[
        ('rf_behavior_model.joblib', '.'),
        ('rf_artifact_model.joblib', '.'),
        ('xgb_behavior_model.joblib', '.'),
        ('xgb_artifact_model.joblib', '.'),
        ('fusion_model.joblib', '.'),
    ],"""
    
    new_datas = f"""datas=[
        ('rf_behavior_model.joblib', '.'),
        ('rf_artifact_model.joblib', '.'),
        ('xgb_behavior_model.joblib', '.'),
        ('xgb_artifact_model.joblib', '.'),
        ('fusion_model.joblib', '.'),
        (r'{mscerts_path}', 'mscerts'),
    ],"""
    
    content = content.replace(old_datas, new_datas)
    
    # Write back
    with open('build_config.spec', 'w') as f:
        f.write(content)
    
    print("✅ build_config.spec updated with mscerts path")
    print(f"   Path: {mscerts_path}")
else:
    print("✅ mscerts already in build_config.spec")

print("\nNext steps:")
print("1. rmdir /s build dist")
print("2. pyinstaller build_config.spec --clean")
print("3. makensis installer.nsi")
```

Run it:
```cmd
python fix_mscerts.py
```

---

## Step 4: Rebuild
```cmd
rmdir /s build dist
pyinstaller build_config.spec --clean
makensis installer.nsi
```

---

## If All Else Fails: Remove mscerts Dependency

The simplest solution - modify your code to not use mscerts:

### On Windows, edit `static_feature_extractor.py`:

Find any lines with `mscerts` or `certvalidator` and comment them out:

```python
# OLD:
# from certvalidator import CertificateValidator
# from mscerts import get_certs

# NEW:
# Commented out - using alternative method
```

Then rebuild:
```cmd
rmdir /s build dist
pyinstaller build_config.spec --clean
makensis installer.nsi
```

This way the app works without signature validation (still scans, just skips cert checking).

---

## Quick Fix Summary

**Option 1: Auto-fix script (RECOMMENDED)**
```cmd
python fix_mscerts.py
rmdir /s build dist
pyinstaller build_config.spec --clean
makensis installer.nsi
```

**Option 2: Manual fix**
1. Run: `python -c "import mscerts, os; print(os.path.dirname(mscerts.__file__))"`
2. Copy the path
3. Add to build_config.spec datas section
4. Rebuild

**Option 3: Nuclear option (removes dependency)**
1. Comment out mscerts imports in source
2. Rebuild
3. Works but skips signature validation

Try Option 1 first!
