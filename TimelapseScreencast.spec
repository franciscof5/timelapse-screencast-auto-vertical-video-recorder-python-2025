# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['timelapse-screencast.py'],
    pathex=['venv/lib/python3.12/site-packages'],
    binaries=[],
    datas=[('venv/lib/python3.12/site-packages/pystray', 'pystray')],
    hiddenimports=['pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TimelapseScreencast',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='TimelapseScreencast.app',
    icon=None,
    bundle_identifier=None,
)
