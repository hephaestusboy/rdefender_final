# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for R-Defender

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
        ('gui', 'gui'),
        (r'C:\Users\vboxuser\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\mscerts', 'mscerts'),
        (r'C:\Users\vboxuser\Desktop\rdefender_final\rdefender_final\venv\Lib\site-packages\xgboost', 'xgboost'),
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
        'joblib',
        'numpy',
        'scipy',
        'watchdog',
        'psutil',
	'mscerts',
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

