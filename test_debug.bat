@echo off
echo Probando Inventario GHL con Debug Output
echo ========================================
echo.
echo Directorio actual: %CD%
echo.

if exist "dist\nuitka-onedir\main.dist\InventarioGHL.exe" (
    echo Ejecutando con debug output...
    echo Presiona Ctrl+C para salir cuando termine
    echo.
    "dist\nuitka-onedir\main.dist\InventarioGHL.exe"
    echo.
    echo Aplicacion terminada con codigo: %ERRORLEVEL%
) else (
    echo Ejecutable no encontrado en: dist\nuitka-onedir\main.dist\InventarioGHL.exe
    echo Ejecuta: uv run python build_nuitka.py onedir
)

pause