@echo off
REM Build VoiceVibe.exe on Windows, giao dien Qt dep.
REM Tu cai pyinstaller neu chua co, neu loi thi dung lai, khong in Done gia.
python -m pip install -r requirements-qt.txt
if errorlevel 1 goto :error
python -m pip install pyinstaller
if errorlevel 1 goto :error
python -m PyInstaller --onefile --windowed --name VoiceVibe gui_qt.py
if errorlevel 1 goto :error
if not exist dist\VoiceVibe.exe goto :error
echo Done: dist\VoiceVibe.exe
pause
exit /b 0
:error
echo Build THAT BAI. Hay chay: python -m pip install pyinstaller
pause
exit /b 1
