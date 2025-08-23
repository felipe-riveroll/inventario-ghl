#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Inventario GHL.
"""
import os
import sys

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.main_window_optimized import main

if __name__ == "__main__":
    main()