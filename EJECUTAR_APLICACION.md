# Como Ejecutar la Aplicación Inventario GHL

## Ejecutables Compilados

Después de compilar con Nuitka, tienes dos versiones disponibles:

### 1. Versión Onefile (Recomendada)
```bash
# Desde PowerShell:
.\dist\nuitka\InventarioGHL.exe

# Desde Command Prompt:
dist\nuitka\InventarioGHL.exe

# Usando el script de prueba:
.\test_onefile.bat
```

**Características:**
- ✅ Un solo archivo ejecutable
- ✅ Fácil de distribuir
- ✅ Tamaño: ~23.4 MB
- ✅ Incluye todas las dependencias

### 2. Versión Standalone
```bash
# Desde PowerShell:
.\dist\main.dist\main.exe

# Desde Command Prompt:
dist\main.dist\main.exe

# Usando el script de prueba:
.\test_standalone.bat
```

**Características:**
- ✅ Archivos separados (más rápido de crear)
- ✅ Incluye todas las dependencias en carpeta
- ⚠️ Requiere mantener toda la carpeta `main.dist`

## Scripts de Prueba Disponibles

### Batch Scripts (Windows)
- `test_onefile.bat` - Prueba la versión onefile
- `test_standalone.bat` - Prueba la versión standalone  
- `test_build.bat` - Información sobre builds existentes

### PowerShell Script
- `test_executables.ps1` - Script completo con menús interactivos

```powershell
# Para ejecutar el script PowerShell:
.\test_executables.ps1
```

## Solución de Problemas

### Error "The module '.dist' could not be loaded"

Este error ocurre por sintaxis incorrecta en PowerShell. **Soluciones:**

1. **Usar la sintaxis correcta:**
   ```powershell
   # ✅ Correcto:
   .\dist\nuitka\InventarioGHL.exe
   
   # ❌ Incorrecto:
   .dist\nuitka\InventarioGHL.exe  # Missing backslash
   ```

2. **Usar ruta completa:**
   ```powershell
   & "C:\Users\felipillo\proyectos\inventario-ghl\dist\nuitka\InventarioGHL.exe"
   ```

3. **Usar Command Prompt en lugar de PowerShell:**
   ```cmd
   dist\nuitka\InventarioGHL.exe
   ```

### La Aplicación No Encuentra el Archivo .env

La aplicación busca el archivo `.env` en este orden:

1. **Directorio de trabajo actual** (donde ejecutas el comando)
2. **Directorio del ejecutable**
3. **Archivo `.env` relativo**

**Solución:** Ejecuta siempre desde el directorio raíz del proyecto:

```powershell
# Asegúrate de estar en la carpeta correcta:
cd C:\Users\felipillo\proyectos\inventario-ghl

# Luego ejecuta:
.\dist\nuitka\InventarioGHL.exe
```

### Las Credenciales No Se Guardan

Si después del flujo OAuth las credenciales no se guardan:

1. **Verifica permisos de escritura** en la carpeta
2. **Ejecuta como administrador** si es necesario
3. **Revisa que existe un archivo `.env`** o crea uno vacío

```bash
# Crear archivo .env vacío si no existe:
echo "# Configuración Inventario GHL" > .env
```

## Desarrollo vs Producción

### Modo Desarrollo
```bash
uv run python main.py
```

### Modo Producción (Compilado)
```bash
.\dist\nuitka\InventarioGHL.exe
```

## Recomendaciones para Distribución

1. **Usa la versión onefile** para distribución
2. **Incluye instrucciones** sobre dónde ejecutar
3. **Proporciona un .env de ejemplo** con las claves necesarias
4. **Documenta los permisos** necesarios (escribir archivos)

## Compilación

Para recompilar la aplicación:

```bash
# Versión onefile (recomendada):
uv run python build_nuitka.py build

# Versión standalone (desarrollo):
uv run python build_nuitka.py onedir
```

El script automáticamente creará los scripts de prueba después de compilar.