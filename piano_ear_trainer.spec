# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Piano Ear Trainer."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Путь к проекту
project_dir = Path(SPECPATH)

# Собираем все данные и модули PySide6
pyside6_datas = collect_data_files('PySide6', include_py_files=False)
pyside6_imports = collect_submodules('PySide6')

a = Analysis(
    [str(project_dir / 'piano_ear_trainer' / 'app.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # Включаем MP3 сэмплы
        (str(project_dir / 'assets' / 'samples_mp3'), 'assets/samples_mp3'),
    ] + pyside6_datas,
    hiddenimports=[
        'pygame',
    ] + pyside6_imports,
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
    name='PianoEarTrainer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Временно для отладки
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Можно добавить иконку: icon='assets/icon.ico'
)
