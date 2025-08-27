# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a desktop application for generating inventory reports from the HighLevel API using PySide6 and XlsxWriter. The application features an integrated OAuth2 flow, background processing, and professional Excel report generation with embedded images.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --dev
```

### Running the Application
```bash
# Run the main application
uv run python main.py
```

### Code Quality and Linting
```bash
# Check code with ruff
uv run ruff check src/

# Format code with ruff
uv run ruff format src/

# Check specific file
uv run ruff check src/main_window_optimized.py
```

### Building Executable

#### Option 1: Nuitka (Recommended - Better performance)
```bash
# Build optimized single-file executable with Nuitka
uv run python build_nuitka.py build

# Alternative: Build as directory (faster compilation for development)
uv run python build_nuitka.py onedir

# Output will be in: dist/nuitka/InventarioGHL.exe
```

#### Option 2: cx_Freeze (Legacy)
```bash
# Build executable for distribution
uv run python build_exe.py build

# Output will be in: dist/InventarioGHL/
```

## Architecture and Code Structure

### Main Components

1. **Entry Point**: `main.py` - Sets up Python path and launches the optimized main window
2. **Core Application**: `src/main_window_optimized.py` - Main GUI with integrated OAuth2 flow
3. **API Client**: `src/highlevel_api.py` - Handles HighLevel API communication with multiple endpoint fallbacks
4. **Excel Generator**: `src/excel_generator_xlsx.py` - Creates formatted Excel reports using XlsxWriter

### Key Architectural Patterns

- **Threading**: Uses QThread workers (`InventoryWorker`, `ExcelWorker`) for non-blocking API calls and Excel generation
- **Signal-Slot Communication**: PySide6 signals connect background workers to UI updates
- **Fallback Strategy**: API client tries multiple endpoints with different parameter combinations
- **OAuth2 Integration**: Built-in web server for handling OAuth2 callbacks on localhost:8080

### Configuration Management

The application uses environment variables loaded via python-dotenv:
- `HIGHLEVEL_ACCESS_TOKEN` - OAuth2 access token
- `HIGHLEVEL_LOCATION_ID` - HighLevel location identifier  
- `HIGHLEVEL_API_VERSION` - API version (defaults to "2021-07-28")

### Excel Report Features

- Professional formatting with colors, borders, and alternating row styles
- Embedded images using Excel IMAGE() formulas
- Automatic column width adjustment
- Summary statistics (total products, quantities, generation date)
- Instructions for activating images in Excel (requires Ctrl+L find/replace)

### Error Handling Strategy

- API client implements comprehensive endpoint fallback with different parameter sets
- Worker threads emit error signals to prevent UI crashes
- User-friendly error dialogs with specific troubleshooting information
- Connection testing functionality before data operations

## Important Implementation Notes

- The main window uses `main_window_optimized.py`, not `main_window.py`
- API endpoints are probed systematically with different parameter combinations (`locationId` vs `altId/altType`)
- Excel generation uses XlsxWriter (not openpyxl) for better performance and features
- OAuth2 flow uses a temporary local web server that automatically shuts down after token retrieval
- Images in Excel require manual activation via find/replace to convert IMAGE formulas