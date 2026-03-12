# 🛡️ Advanced Fix: mscerts FileNotFoundError

## Problem
Even with `mscerts` in hiddenimports, still getting:
```
FileNotFoundError: \\mscerts\\authroot.stl
```

## Reason
`mscerts` has data files (not just Python code) that need to be bundled as `datas`, not `hiddenimports`.

---

## ✅ Solution: Bundle mscerts Data Files

### Step 1: Find mscerts Location

On Windows Command Prompt:
```cmd
python -c "import mscerts; import os; print(os.path.dirname(mscerts.__file__))"
```

This will output something like:
```
C:\Users\YourName\AppData\Local\Programs\Python\Python314\Lib\site-packages\mscerts
```

**Copy this path** - you'll need it.

### Step 2: Update build_config.spec

Edit your `build_config.spec` file:

**Find the `datas` section:**
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
],
```

**Add mscerts data files:**
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
    # Add this line (replace with your actual path from Step 1):
    (r'C:\path\to\mscerts', 'mscerts'),
],
```

**Example with actual path:**
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
    (r'C:\Users\YourName\AppData\Local\Programs\Python\Python314\Lib\site-packages\mscerts', 'mscerts'),
],
```

### Step 3: Rebuild Everything

```cmd
rmdir /s build dist
pyinstaller build_config.spec --clean
makensis installer.nsi
```

### Step 4: Uninstall and Reinstall

- Uninstall old version via Add/Remove Programs
- Run new `RDefender-Setup.exe`
- Test ✅

---

## Alternative Solution: Disable Signature Validation

If the above doesn't work, you can disable the feature that uses mscerts:

### Option A: Modify rdefender_agent.py (Quick Fix)

Find where certificates are validated and comment it out:

```python
# Search for: IS_SIGNATURE_VALID, certvalidator, or mscerts
# Comment out those lines or set to 0
```

### Option B: Use certifi Instead

Replace mscerts with certifi (which is easier to bundle):

```cmd
pip uninstall mscerts
pip install certifi
```

Then in your code:
```python
import certifi
cert_path = certifi.where()
```

---

## Complete build_config.spec Template

Here's a complete fixed version with everything:

```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['rdefender_ui_clr_copy.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('rf_behavior_model.joblib', '.'),
        ('rf_artifact_model.joblib', '.'),
        ('xgb_behavior_model.joblib', '.'),
        ('xgb_artifact_model.joblib', '.'),
        ('fusion_model.joblib', '.'),
        # IMPORTANT: Replace with your actual mscerts path from Step 1
        (r'C:\YOUR\ACTUAL\PATH\TO\mscerts', 'mscerts'),
    ],
    hiddenimports=[
        'sklearn',
        'sklearn.ensemble',
        'sklearn.tree',
        'xgboost',
        'joblib',
        'numpy',
        'watchdog',
        'psutil',
        'mscerts',
        'certvalidator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RDefender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RDefender',
)
```

---

## Fastest Option: Use certifi

If you want the quickest fix:

### Step 1: Install certifi
```cmd
pip install certifi
```

### Step 2: Update build_config.spec
```python
datas=[
    ('rf_behavior_model.joblib', '.'),
    ('rf_artifact_model.joblib', '.'),
    ('xgb_behavior_model.joblib', '.'),
    ('xgb_artifact_model.joblib', '.'),
    ('fusion_model.joblib', '.'),
],
hiddenimports=[
    'sklearn',
    'sklearn.ensemble',
    'sklearn.tree',
    'xgboost',
    'joblib',
    'numpy',
    'watchdog',
    'psutil',
    'certifi',
],
```

### Step 3: Update rdefender_agent.py
Find the line that uses mscerts and replace with certifi:
```python
# OLD:
# import mscerts

# NEW:
import certifi
```

### Step 4: Rebuild
```cmd
rmdir /s build dist
pyinstaller build_config.spec --clean
makensis installer.nsi
```

---

## Checklist

- [ ] Found mscerts path: `python -c "import mscerts; import os; print(os.path.dirname(mscerts.__file__))"`
- [ ] Updated datas in build_config.spec with correct path
- [ ] Deleted build and dist folders
- [ ] Ran: `pyinstaller build_config.spec --clean`
- [ ] Ran: `makensis installer.nsi`
- [ ] Uninstalled old version
- [ ] Installed new RDefender-Setup.exe
- [ ] Tested - no errors ✅

---

## Still Not Working?

Try this diagnostic on Windows:

```cmd
# Check if mscerts is properly installed
python -c "import mscerts; print('mscerts OK')"

# Check if authroot.stl exists
python -c "import mscerts, os; print(os.path.join(os.path.dirname(mscerts.__file__), 'authroot.stl'))"

# If the second command shows the file exists, use that path in build_config.spec
```

---

## Nuclear Option: Remove mscerts Dependency

If all else fails, modify the source code to not use mscerts:

Edit `static_feature_extractor.py` or `rdefender_agent.py`:

Search for `mscerts` and either:
1. Comment it out
2. Replace with dummy implementation
3. Wrap in try/except

This is the last resort - the app will still work, just without signature validation.

---

Let me know which approach you want to try first!
