#!/usr/bin/env python3
"""
Script para compilar la aplicación a ejecutable usando cx_Freeze.
"""
import sys
from cx_Freeze import Executable, setup

# Archivos a incluir
include_files = [
    ".env.example",
]

# Paquetes a incluir
packages = [
    "PySide6",
    "requests",
    "xlsxwriter", 
    "dotenv",
    "urllib3",
]

# Módulos a excluir para reducir tamaño
excludes = [
    "tkinter",
    "matplotlib",
    "numpy",
    "pandas",
    "jupyter",
    "IPython",
]

# Configuración del ejecutable
executables = [
    Executable(
        "main.py",
        base="Win32GUI",  # Para aplicaciones GUI en Windows
        target_name="InventarioGHL.exe",
        icon=None,  # Puedes agregar un icono .ico aquí
        shortcut_name="Inventario GHL",
        shortcut_dir="DesktopFolder",
    )
]

# Configuración de build
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "include_msvcrt": True,
    "optimize": 2,
    "build_exe": "dist/InventarioGHL",
}

setup(
    name="InventarioGHL",
    version="2.0.0",
    description="Generador de reportes de inventario para HighLevel",
    author="Tu Nombre",
    options={"build_exe": build_exe_options},
    executables=executables,
)