#!/usr/bin/env python3
"""
Punto de entrada principal para la aplicación Inventario GHL.
"""
import os
import sys

def get_resource_path():
    """Obtiene la ruta base para recursos, funciona tanto en desarrollo como ejecutable compilado"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Si está ejecutándose como ejecutable compilado (PyInstaller)
        return sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        # Si está ejecutándose como ejecutable compilado (otros empaquetadores)
        return os.path.dirname(sys.executable)
    else:
        # Si está ejecutándose como script Python normal
        return os.path.dirname(os.path.abspath(__file__))

# Obtener la ruta base
base_path = get_resource_path()

# Cargar variables de entorno antes de importar otros módulos
from dotenv import load_dotenv

# Intentar cargar .env desde diferentes ubicaciones
env_paths = [
    os.path.join(base_path, ".env"),
    os.path.join(os.getcwd(), ".env"),
    ".env"
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Agregar el directorio src al path para importar módulos
if not getattr(sys, 'frozen', False):
    # Solo agregar src al path si no estamos ejecutándose como compilado
    sys.path.insert(0, os.path.join(base_path, "src"))

from src.main_window_optimized import main

if __name__ == "__main__":
    main()