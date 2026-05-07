# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for R-Defender v6

block_cipher = None

# Resolve site-packages path at spec-parse time so the spec is portable
import sys, os, platform
_sp = next(p for p in sys.path if 'site-packages' in p and os.path.isdir(p))
_win = platform.system() == 'Windows'

# Native binaries — Linux uses .so, Windows PyInstaller hooks handle DLLs automatically
_binaries = []
if not _win:
    _xgb_so = os.path.join(_sp, 'xgboost', 'lib', 'libxgboost.so')
    if os.path.exists(_xgb_so): _binaries.append((_xgb_so, 'xgboost/lib'))

# Bundle mscerts package — contains authroot.stl and cacert.pem required by signify at runtime
try:
    import mscerts
    _mscerts_dir = os.path.dirname(mscerts.__file__)
except Exception:
    _mscerts_dir = os.path.join(_sp, 'mscerts')

_datas = [
    # v6 models
    ('rf_behavior_model_v6.joblib', '.'),
    ('rf_artifact_model_v6.joblib', '.'),
    ('xgb_behavior_model_v6.joblib', '.'),
    ('xgb_artifact_model_v6.joblib', '.'),
    ('fusion_model_v6.joblib', '.'),
    ('thresholds_v6.json', '.'),
    # GUI
    ('gui', 'gui'),
    # xgboost package tree so runtime imports resolve
    (os.path.join(_sp, 'xgboost'), 'xgboost'),
    # mscerts — authroot.stl + cacert.pem needed by signify.authenticode.trust_list
    (_mscerts_dir, 'mscerts'),
]

a = Analysis(
    ['rdefender_ui_clr_copy.py'],
    pathex=[],
    binaries=_binaries,
    datas=_datas,
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
        'signify',
        'signify.authenticode',
        'signify.authenticode.cert_store',
        'signify.authenticode.trust_list',
        'signify.pkcs7',
        'signify.x509',
        'mscerts',
        'mscerts.core',
        'certifi',
        'asn1crypto',
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

