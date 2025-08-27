# CRUSH.md

## Commands
- **Run app**: `uv run python main.py`
- **Build (Nuitka, single‑file)**: `uv run python build_nuitka.py build`
- **Build (Nuitka, directory)**: `uv run python build_nuitka.py onedir`
- **Build (cx_Freeze)**: `uv run python build_exe.py build`
- **Lint**: `uv run ruff check src/`
- **Format**: `uv run ruff format src/`
- **Run tests**: `uv run pytest` (add `-k <test_name>` to run a single test)

## Code style guidelines
- **Imports**: stdlib → third‑party → local, separated by a blank line. No wildcard imports.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- **Typing**: use `from typing import ...` and annotate all public functions.
- **Docstrings**: triple double quotes, include *Args*, *Returns*, *Raises* sections.
- **Line length**: 88 characters (as enforced by Black/Ruff).
- **Formatting**: run Black via `ruff format`; keep trailing commas, use f‑strings.
- **Error handling**: validate env vars early, raise `ValueError` with clear messages; wrap external calls in `try/except` and re‑raise with context.
- **Logging**: use `print` for simple CLI feedback or the `logging` module for production code.

## Misc
- No hidden `.cursor` or Copilot rule files detected, but if added, include them here.
- Keep the `src/` package importable (`import src.module`).
