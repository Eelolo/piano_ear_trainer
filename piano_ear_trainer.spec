# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Piano Ear Trainer."""

import sys
from pathlib import Path

block_cipher = None

# Путь к проекту
project_dir = Path(SPECPATH)

# Иконки
icon_files = [
    (str(project_dir / 'assets' / 'icon.ico'), 'assets'),
    (str(project_dir / 'assets' / 'icon.png'), 'assets'),
]
if sys.platform == 'darwin':
    icon_files.append((str(project_dir / 'assets' / 'icon.icns'), 'assets'))

a = Analysis(
    [str(project_dir / 'piano_ear_trainer' / 'app.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        (str(project_dir / 'assets' / 'samples_mp3'), 'assets/samples_mp3'),
    ] + icon_files,
    hiddenimports=[
        'pygame',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebChannel',
        'PySide6.QtNetwork',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.Qt3D',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
    ],
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
    name='PianoEarTrainer',
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
    icon=str(project_dir / 'assets' / ('icon.icns' if sys.platform == 'darwin' else 'icon.ico')),
)

# macOS: создаём .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PianoEarTrainer.app',
        icon=str(project_dir / 'assets' / 'icon.icns'),
        bundle_identifier='com.pianoeartrainer.app',
        info_plist={
            'CFBundleName': 'Piano Ear Trainer',
            'CFBundleDisplayName': 'Piano Ear Trainer',
            'CFBundleShortVersionString': '0.1.0',
            'NSHighResolutionCapable': True,
        },
    )
