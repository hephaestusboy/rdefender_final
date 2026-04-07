# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for R-Defender

block_cipher = None

# Resolve site-packages path at spec-parse time so the spec is portable
import sys, os, platform
_sp = next(p for p in sys.path if 'site-packages' in p and os.path.isdir(p))
_win = platform.system() == 'Windows'

# Native binaries — Linux uses .so, Windows PyInstaller hooks handle DLLs automatically
_binaries = []
if not _win:
    _xgb_so = os.path.join(_sp, 'xgboost', 'lib', 'libxgboost.so')
    _cat_so  = os.path.join(_sp, 'catboost', '_catboost.so')
    if os.path.exists(_xgb_so): _binaries.append((_xgb_so, 'xgboost/lib'))
    if os.path.exists(_cat_so):  _binaries.append((_cat_so, 'catboost'))

a = Analysis(
    ['rdefender_ui_clr_copy.py'],
    pathex=[],
    binaries=_binaries,
    datas=[
        # v5 base models
        ('rf_behavior_model_v5.joblib', '.'),
        ('rf_artifact_model_v5.joblib', '.'),
        ('xgb_behavior_model_v5.joblib', '.'),
        ('xgb_artifact_model_v5.joblib', '.'),
        ('lgbm_behavior_model_v5.joblib', '.'),
        ('lgbm_artifact_model_v5.joblib', '.'),
        ('catboost_behavior_model_v5.joblib', '.'),
        ('catboost_artifact_model_v5.joblib', '.'),
        ('fusion_model_v5.joblib', '.'),
        ('thresholds_v5.json', '.'),
        # GUI
        ('gui', 'gui'),
        # full package trees so runtime imports resolve
        (os.path.join(_sp, 'xgboost'), 'xgboost'),
        (os.path.join(_sp, 'lightgbm'), 'lightgbm'),
        (os.path.join(_sp, 'catboost'), 'catboost'),
    ],
    hiddenimports=[
        'sklearn',
        'sklearn.ensemble',
        'sklearn.tree',
        'sklearn.calibration',
        'sklearn.preprocessing',
        'sklearn.linear_model',
        'sklearn.metrics',
        'sklearn.base',
        'sklearn.utils',
        'sklearn.exceptions',
        'xgboost',
        'xgboost.sklearn',
        'lightgbm',
        'lightgbm.sklearn',
        'catboost',
        'catboost.core',
        'joblib',
        'numpy',
        'scipy',
        'watchdog',
        'psutil',
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
    console=False,  # Set to False for GUI only (no console window)
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='rdefender_icon.ico',  # Optional: add an icon
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

#edited

