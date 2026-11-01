@echo off
REM Build VoiceVibe.exe on Windows, giao dien Qt dep:
REM   python -m pip install -r requirements-qt.txt
REM   pip install pyinstaller
pyinstaller --onefile --windowed --name VoiceVibe gui_qt.py
echo Done: dist\VoiceVibe.exe
pause
