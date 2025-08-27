@echo off
echo Testing Nuitka Onefile Executable
echo ===================================
echo.
echo Current directory: %CD%
echo.

if not exist "dist\nuitka\InventarioGHL.exe" (
    echo ERROR: Executable not found!
    echo Expected: dist\nuitka\InventarioGHL.exe
    echo.
    echo Run: uv run python build_nuitka.py build
    pause
    exit /b 1
)

echo File size:
for %%I in ("dist\nuitka\InventarioGHL.exe") do echo   %%~zI bytes (%%~nxI)
echo.

echo Starting executable...
echo Press any key to continue or Ctrl+C to cancel
pause > nul

"dist\nuitka\InventarioGHL.exe"

echo.
echo Executable finished with exit code: %ERRORLEVEL%
pause