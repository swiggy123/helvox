# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/helvox/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('src/helvox/resources', 'helvox/resources')],
    hiddenimports=[
        'pkg_resources',
        'pkg_resources.extern',
        'pkg_resources.extern.packaging',
        'pkg_resources.extern.platformdirs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Helvox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
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
    upx=False,
    upx_exclude=[],
    name='Helvox',
)

app = BUNDLE(
    coll,
    name='Helvox.app',
    icon=None,
    bundle_identifier='io.noxenum.helvox',
    info_plist={
        'NSMicrophoneUsageDescription': 'Helvox needs microphone access to record speech samples.',
    },
)
