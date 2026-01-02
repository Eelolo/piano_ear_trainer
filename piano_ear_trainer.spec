# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Ear Trainer."""

import sys
from pathlib import Path

block_cipher = None

# Путь к проекту
project_dir = Path(SPECPATH)

a = Analysis(
    [str(project_dir / 'piano_ear_trainer' / 'app.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # Включаем MP3 сэмплы
        (str(project_dir / 'assets' / 'samples_mp3'), 'assets/samples_mp3'),
    ],
    hiddenimports=[
        'pygame',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='EarTrainer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консольного окна
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Можно добавить иконку: icon='assets/icon.ico'
)
