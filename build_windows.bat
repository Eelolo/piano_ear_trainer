@echo off
echo === Building Ear Trainer for Windows ===

REM Установка зависимостей
echo Installing dependencies...
pip install PySide6 pygame pyinstaller

REM Сборка
echo Building executable...
pyinstaller piano_ear_trainer.spec --clean

echo.
echo === Build complete! ===
echo Executable: dist\EarTrainer.exe
pause
