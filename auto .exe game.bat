@echo off
echo Building DinoGame.exe...
pyinstaller --noconfirm --onefile --windowed --icon "assets/images/icon.png" --add-data "assets;assets" --add-data "config-feedforward.txt;." "src/main.py"

echo Cleaning up temp files...
move /y dist\main.exe DinoGame.exe
rmdir /s /q build
rmdir /s /q dist
del /q main.spec

echo Done! DinoGame.exe created in root folder.
pause