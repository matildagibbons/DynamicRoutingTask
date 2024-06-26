@echo off

REM Set the display mode to duplicate on monitors 1 and 2
echo Selecting duplicate display mode...
"C:\Windows\System32\DisplaySwitch.exe" /clone

REM Optional: Add a pause to view the result
pause