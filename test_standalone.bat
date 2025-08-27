@echo off
echo Testing Nuitka Standalone Executable
echo ====================================
echo.
echo Current directory: %CD%
echo.

if not exist "dist\main.dist\main.exe" (
    echo ERROR: Executable not found!
    echo Expected: dist\main.dist\main.exe
    echo.
    echo Run: uv run nuitka --standalone --windows-console-mode=force --enable-plugin=pyside6 --output-dir=dist --remove-output --no-prefer-source-code main.py
    pause
    exit /b 1
)

echo Directory contents:
dir "dist\main.dist" | findstr /V "Directory"
echo.

echo Starting executable...
echo Press any key to continue or Ctrl+C to cancel
pause > nul

"dist\main.dist\main.exe"

echo.
echo Executable finished with exit code: %ERRORLEVEL%
pause