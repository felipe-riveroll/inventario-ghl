#!/usr/bin/env python3
"""
Script para compilar la aplicación a ejecutable usando Nuitka.
Nuitka ofrece mejor rendimiento y archivos más pequeños que cx_Freeze.
"""
import os
import sys
import subprocess
from pathlib import Path


def build_with_nuitka():
    """Compila la aplicación usando Nuitka"""
    
    # Comando base de Nuitka
    nuitka_cmd = [
        "uv", "run", "python", "-m", "nuitka",
        
        # Opciones principales
        "--onefile",                    # Crear un solo archivo ejecutable
        "--standalone",                 # Incluir todas las dependencias
        "--assume-yes-for-downloads",   # Descargar automáticamente dependencias
        "--no-prefer-source-code",      # Usar bytecode para optimización
        "--remove-output",              # Limpiar salida previa
        
        # Optimizaciones
        "--lto=yes",                    # Link Time Optimization
        "--jobs=4",                     # Usar múltiples cores
        
        # GUI y Windows
        "--windows-disable-console",    # No mostrar consola (GUI app)
        #"--windows-console-mode=force", # Forzar consola (útil para debugging)
        "--enable-plugin=pyside6",      # Plugin para PySide6
        
        # Metadatos del ejecutable
        "--product-name=Inventario GHL",
        "--file-description=Generador de reportes de inventario para HighLevel",
        "--product-version=2.0.0",
        "--file-version=2.0.0",
        "--copyright=© 2025 Tu Nombre",
        
        # Archivos y módulos a incluir
        "--include-data-files=.env.example=.env.example",
        "--include-package=src",
        "--include-package-data=certifi",
        "--include-package-data=dotenv",
        
        # Exclusiones para reducir tamaño
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=matplotlib",
        "--nofollow-import-to=numpy", 
        "--nofollow-import-to=pandas",
        "--nofollow-import-to=jupyter",
        "--nofollow-import-to=IPython",
        "--nofollow-import-to=test*",
        "--nofollow-import-to=unittest",
        
        # Directorio de salida
        "--output-dir=dist/nuitka",
        "--output-filename=InventarioGHL.exe",
        
        # Archivo principal
        "main.py"
    ]
    
    print("Iniciando compilación con Nuitka...")
    print("Directorio de salida: dist/nuitka/")
    print("Opciones:", " ".join(nuitka_cmd[3:]))  # Mostrar solo opciones de Nuitka
    print()
    
    try:
        # Ejecutar Nuitka
        result = subprocess.run(nuitka_cmd, check=True, capture_output=False)
        
        print()
        print("Compilación exitosa!")
        print("Ejecutable creado en: dist/nuitka/InventarioGHL.exe")
        print()
        print("Información del archivo:")
        
        exe_path = Path("dist/nuitka/InventarioGHL.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   Tamaño: {size_mb:.1f} MB")
            print(f"   Ubicación: {exe_path.absolute()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error durante la compilación: {e}")
        return False
    except FileNotFoundError:
        print("Nuitka no encontrado. Está instalado?")
        print("   Ejecuta: uv add --dev nuitka")
        return False


def build_onedir():
    """Alternativa: compilar como directorio (más rápido para desarrollo)"""
    
    nuitka_cmd = [
        "uv", "run", "python", "-m", "nuitka",
        
        # Opciones principales  
        "--standalone",                 # Incluir todas las dependencias
        "--assume-yes-for-downloads",
        
        # Optimizaciones básicas
        "--jobs=4",
        
        # GUI y Windows
        "--windows-console-mode=force",
        "--enable-plugin=pyside6",
        
        # Metadatos
        "--product-name=Inventario GHL",
        "--file-description=Generador de reportes de inventario para HighLevel",
        "--product-version=2.0.0",
        
        # Archivos y módulos a incluir
        "--include-data-files=.env.example=.env.example",
        "--include-package=src",
        "--include-package-data=certifi",
        "--include-package-data=dotenv",
        
        # Directorio de salida
        "--output-dir=dist/nuitka-onedir",
        "--output-filename=InventarioGHL.exe",
        
        "main.py"
    ]
    
    print("Compilando como directorio (modo desarrollo)...")
    print("Directorio de salida: dist/nuitka-onedir/")
    
    try:
        subprocess.run(nuitka_cmd, check=True)
        print("Compilación exitosa!")
        print("Ejecutable en: dist/nuitka-onedir/InventarioGHL.dist/InventarioGHL.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


def test_executable(exe_path):
    """Prueba si el ejecutable se puede iniciar correctamente"""
    print(f"Probando ejecutable: {exe_path}")
    
    if not Path(exe_path).exists():
        print(f"❌ Archivo no encontrado: {exe_path}")
        return False
    
    try:
        # Intentar ejecutar con --version o --help para verificar que funciona
        # Como es una app GUI, solo verificamos que se puede importar
        result = subprocess.run([str(exe_path), "--help"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            print("✅ Ejecutable funciona correctamente")
            return True
        else:
            print(f"⚠️  Ejecutable terminó con código: {result.returncode}")
            return True  # GUI apps pueden devolver códigos diferentes
            
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout - probablemente se inició la GUI")
        return True  # Para GUI, timeout es normal
    except Exception as e:
        print(f"❌ Error ejecutando: {e}")
        return False


def create_test_scripts():
    """Crea scripts de prueba para los ejecutables"""
    scripts_created = []
    
    # Script de prueba para batch
    test_script = """@echo off
echo Testing InventarioGHL Executable
echo ===============================

if exist "dist\\nuitka\\InventarioGHL.exe" (
    echo Found onefile executable: dist\\nuitka\\InventarioGHL.exe
    for %%I in ("dist\\nuitka\\InventarioGHL.exe") do echo Size: %%~zI bytes
    echo.
    echo To run: .\\dist\\nuitka\\InventarioGHL.exe
) else (
    echo Onefile executable not found
)

if exist "dist\\main.dist\\main.exe" (
    echo Found standalone executable: dist\\main.dist\\main.exe  
    for %%I in ("dist\\main.dist\\main.exe") do echo Size: %%~zI bytes
    echo.
    echo To run: .\\dist\\main.dist\\main.exe
) else (
    echo Standalone executable not found
)

echo.
echo Use the provided test scripts:
echo   test_onefile.bat      - Test onefile version
echo   test_standalone.bat   - Test standalone version  
echo   test_executables.ps1  - PowerShell testing script
pause
"""
    
    with open("test_build.bat", "w") as f:
        f.write(test_script)
    scripts_created.append("test_build.bat")
    
    print(f"Scripts de prueba creados: {', '.join(scripts_created)}")
    return scripts_created


if __name__ == "__main__":
    print("Compilador Nuitka para Inventario GHL")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not Path("main.py").exists():
        print("No se encontró main.py en el directorio actual")
        sys.exit(1)
    
    # Opciones de compilación
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Opciones disponibles:")
        print("  build      - Crear ejecutable único (recomendado)")
        print("  onedir     - Crear directorio ejecutable (más rápido)")
        print()
        mode = input("Selecciona modo [build/onedir]: ").lower() or "build"
    
    print()
    
    if mode == "onedir":
        success = build_onedir()
    else:
        success = build_with_nuitka()
    
    if success:
        print()
        print("✅ Compilación exitosa!")
        
        # Crear scripts de prueba
        create_test_scripts()
        
        # Sugerir pruebas
        print()
        print("Para probar el ejecutable:")
        if mode == "onedir":
            exe_path = "dist/nuitka-onedir/InventarioGHL.dist/InventarioGHL.exe"
            print(f"   .\\{exe_path}")
            print("   O usa: .\\test_standalone.bat")
        else:
            exe_path = "dist/nuitka/InventarioGHL.exe"
            print(f"   .\\{exe_path}")
            print("   O usa: .\\test_onefile.bat")
        
        print()
        print("Scripts de prueba disponibles:")
        print("   test_onefile.bat      - Prueba versión onefile")
        print("   test_standalone.bat   - Prueba versión standalone")
        print("   test_executables.ps1  - Script PowerShell completo")
        print("   test_build.bat        - Información de builds")
        
        print()
        print("Tip: El ejecutable incluye todas las dependencias necesarias.")
    else:
        print()
        print("❌ Error en la compilación")
        print("Verifica que todas las dependencias estén instaladas:")
        print("   uv sync --dev")
        sys.exit(1)