# Inventario GHL - Generador de Reportes v2.0

Aplicación de escritorio para generar reportes de inventario desde la API de HighLevel con interfaz integrada para obtención de tokens OAuth2.

## ✨ Características

- 🖥️ **Interfaz gráfica moderna** con PySide6
- 🔐 **Obtención de token OAuth2 integrada** - Sin scripts externos
- 📊 **Generación de reportes Excel profesionales** con XlsxWriter  
- ⚡ **Procesamiento en segundo plano** - UI nunca se bloquea
- 👁️ **Vista previa de datos** antes de generar reportes
- 🖼️ **Fórmulas IMAGE() limpias** con instrucciones para activar imágenes
- 📋 **Estado visual** del token y configuración
- 🔄 **Configuración flexible** de parámetros de consulta

## 🚀 Instalación y Uso

### Opción 1: Ejecutable (Recomendado)

1. **Descargar ejecutable** desde releases
2. **Ejecutar** `InventarioGHL.exe`
3. **Configurar credenciales** OAuth2 en la interfaz
4. **¡Listo para usar!**

### Opción 2: Desde código fuente

```bash
# Instalar dependencias
uv sync

# Ejecutar aplicación
uv run python main.py
```

## 🔧 Configuración OAuth2

### 1. Crear aplicación en HighLevel
- Ve a **Settings → Integrations → My Apps**
- Crea nueva aplicación
- **Redirect URI:** `http://localhost:8080/callback`  
- **Scopes:** `locations.readonly products.readonly products.write products/prices.readonly products/prices.write`

### 2. Obtener token en la aplicación
1. **Ingresar** Client ID y Client Secret
2. **Clic en** "Obtener Token de Acceso"
3. **Autorizar** en el navegador
4. **¡Token guardado automáticamente!**

## 📊 Uso de la aplicación

### Flujo completo:
1. **📋 Configurar OAuth2** → Obtener token
2. **🔌 Probar conexión** → Verificar API
3. **📥 Obtener datos** → Cargar inventario  
4. **📑 Generar reporte** → Crear archivo Excel
5. **🖼️ Activar imágenes** → Seguir instrucciones en Excel

### Para activar imágenes en Excel:
1. **Seleccionar** columna D (Imagen)
2. **Ctrl+L** (Buscar y Reemplazar)
3. **Buscar:** `=IMAGEN` **Reemplazar:** `=IMAGEN`
4. **Reemplazar todo** → ¡Imágenes activadas!

## 📁 Estructura del proyecto

```
inventario/
├── src/
│   ├── main_window_optimized.py    # Interfaz principal con OAuth2
│   ├── highlevel_api.py            # Cliente API HighLevel  
│   └── excel_generator_xlsx.py     # Generador Excel optimizado
├── main.py                         # Punto de entrada
├── build_exe.py                    # Script de compilación
├── pyproject.toml                  # Configuración del proyecto
└── README.md                       # Este archivo
```

## 🏗️ Compilar ejecutable

```bash
# Instalar dependencias de desarrollo  
uv sync --dev

# Compilar ejecutable
uv run python build_exe.py build

# El ejecutable estará en: dist/InventarioGHL/
```

## 🛠️ Desarrollo

### Comandos útiles:
```bash
# Linting y formato
uv run ruff check src/
uv run ruff format src/

# Sincronizar dependencias
uv sync --dev
```

### Dependencias principales:
- **PySide6** - Interfaz gráfica
- **XlsxWriter** - Generación de Excel  
- **requests** - Comunicación HTTP
- **python-dotenv** - Variables de entorno

## ❓ Solución de problemas

### 🔐 Error de token
- Verificar Client ID y Client Secret
- Regenerar token con scopes correctos
- Comprobar que la app de HighLevel esté activa

### 🌐 Error de conexión
- Verificar conexión a internet
- Confirmar que el Location ID sea correcto
- Revisar estado del servicio de HighLevel

### 📊 Error al generar Excel
- Cerrar Excel si el archivo está abierto
- Verificar permisos de escritura en carpeta destino
- Comprobar espacio disponible en disco

### 🖼️ Las imágenes no aparecen
- Seguir instrucciones en columna F del Excel
- Usar Ctrl+L (Buscar y Reemplazar) en toda la columna D
- Verificar que las URLs de imágenes sean válidas

## 📋 Notas de versión

### v2.0.0
- ✅ OAuth2 integrado en la interfaz
- ✅ Migración de openpyxl a XlsxWriter
- ✅ Fórmulas IMAGE() optimizadas 
- ✅ Scripts externos eliminados
- ✅ Preparado para compilación a ejecutable
- ✅ Código optimizado con ruff

## 📞 Soporte

Para reportar problemas o solicitar características, contacta al equipo de desarrollo.