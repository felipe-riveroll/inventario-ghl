# Inventario GHL - Generador de Reportes

Aplicación de escritorio para generar reportes de inventario desde la API de HighLevel utilizando PySide6 y openpyxl.

## Características

- ✅ Interfaz gráfica moderna con PySide6
- ✅ Conexión directa a la API de HighLevel
- ✅ Generación de reportes en Excel con formato profesional
- ✅ Procesamiento en segundo plano para no bloquear la UI
- ✅ Vista previa de datos antes de generar reportes
- ✅ Configuración flexible de parámetros de consulta

## Instalación

### Prerrequisitos

- Python 3.10 o superior
- UV package manager

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd inventario
   ```

2. **Instalar dependencias con UV**
   ```bash
   uv sync
   ```

3. **Configurar variables de entorno**
   
   Copia el archivo `.env.example` a `.env` y configura tus credenciales:
   ```bash
   cp .env.example .env
   ```
   
   Edita el archivo `.env` con tus datos:
   ```env
   HIGHLEVEL_ACCESS_TOKEN=tu_token_de_acceso
   HIGHLEVEL_LOCATION_ID=tu_location_id
   HIGHLEVEL_API_VERSION=2021-07-28
   API_LIMIT=300
   API_OFFSET=0
   ```

## Uso

### Ejecutar la aplicación

```bash
uv run python main.py
```

### Pasos para generar un reporte

1. **Probar conexión**: Haz clic en "Probar Conexión" para verificar que las credenciales están configuradas correctamente.

2. **Configurar parámetros**: Ajusta el límite de productos y offset según tus necesidades.

3. **Obtener datos**: Haz clic en "Obtener Datos de Inventario" para cargar los productos desde HighLevel.

4. **Generar reporte**: Una vez cargados los datos, haz clic en "Generar Reporte Excel" y selecciona dónde guardar el archivo.

## Estructura del proyecto

```
inventario/
├── src/
│   ├── __init__.py
│   ├── highlevel_api.py      # Cliente para API de HighLevel
│   ├── excel_generator.py    # Generador de reportes Excel
│   └── main_window.py        # Interfaz gráfica principal
├── main.py                   # Punto de entrada
├── pyproject.toml           # Configuración del proyecto
├── .env.example             # Plantilla de variables de entorno
└── README.md               # Este archivo
```

## Configuración de HighLevel

Para obtener tus credenciales de HighLevel:

1. **Access Token**: Ve a tu cuenta de HighLevel → Settings → Integrations → API Keys
2. **Location ID**: Puedes encontrarlo en la URL de tu location o en la configuración de la API
3. **API Version**: Usa "2021-07-28" (versión recomendada)

## Funcionalidades del reporte Excel

El reporte generado incluye:

- **Datos del inventario**: Nombre, nombre de producto, cantidad disponible, URL de imagen
- **Formato profesional**: Encabezados con colores, bordes, filas alternadas
- **Resumen automático**: Total de productos, cantidad total, fecha de generación
- **Ajuste automático**: Ancho de columnas optimizado para mejor visualización

## Desarrollo

### Comandos útiles

```bash
# Instalar dependencias de desarrollo
uv sync --dev

# Formatear código
uv run black src/

# Linting
uv run ruff check src/
```

### Agregar nuevas dependencias

```bash
# Dependencia de producción
uv add nombre-paquete

# Dependencia de desarrollo
uv add --dev nombre-paquete
```

## Solución de problemas

### Error: "HIGHLEVEL_ACCESS_TOKEN no está configurado"
- Verifica que el archivo `.env` existe y tiene las variables correctas
- Asegúrate de que el token de acceso sea válido

### Error de conexión con la API
- Verifica tu conexión a internet
- Confirma que el token y location ID sean correctos
- Revisa que la versión de API sea compatible

### Error al generar Excel
- Verifica que tienes permisos de escritura en la carpeta de destino
- Asegúrate de que el archivo no esté abierto en Excel

## Licencia

Este proyecto es de uso interno. Contacta al desarrollador para más información.

## Soporte

Para reportar problemas o solicitar características, contacta al equipo de desarrollo.