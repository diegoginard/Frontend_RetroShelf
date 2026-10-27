import os
import random
from pathlib import Path

# Directorio raíz del proyecto RetroShelf
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APP_DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "RetroShelf"


def get_layouts_root() -> Path:
    """
    Retorna la ruta a la carpeta 'Layouts' principal.
    Prioriza la carpeta 'Layouts' en la raíz del repositorio/ejecutable.
    Si no existe, busca o crea la carpeta en el directorio de datos de usuario (APPDATA).
    """
    repo_layouts = REPO_ROOT / "Layouts"
    if repo_layouts.is_dir():
        return repo_layouts

    app_layouts = APP_DATA_DIR / "Layouts"
    app_layouts.mkdir(parents=True, exist_ok=True)
    return app_layouts


_THEMES_CACHE: dict[str, dict] | None = None


def get_all_theme_layouts(force_reload: bool = False) -> dict[str, dict]:
    """
    Escanea la carpeta 'Layouts' y registra las subcarpetas de sistemas emulados.
    Cada carpeta de layout maneja de manera 100% autónoma sus propios archivos y recursos.
    """
    global _THEMES_CACHE
    if _THEMES_CACHE is not None and not force_reload:
        return _THEMES_CACHE

    layouts_dir = get_layouts_root()
    themes = {}

    if not layouts_dir.is_dir():
        _THEMES_CACHE = themes
        return themes

    for entry in os.scandir(layouts_dir):
        if not entry.is_dir():
            continue
        if entry.name.startswith((".", "_")):
            continue
        # Solo registrar carpetas que contengan theme_layout.py
        if not (Path(entry.path) / "theme_layout.py").is_file():
            continue

        folder = Path(entry.path)
        themes[entry.name] = {
            "name": entry.name,
            "folder": str(folder),
        }

    _THEMES_CACHE = themes
    return themes


def get_theme_info(theme_name: str) -> dict | None:
    """Obtiene la información básica (nombre y carpeta) de un tema específico."""
    if not theme_name:
        return None
    themes = get_all_theme_layouts()
    if theme_name in themes:
        return themes[theme_name]
    tn_lower = theme_name.lower().strip()
    for name, info in themes.items():
        if tn_lower == name.lower():
            return info
    for name, info in themes.items():
        if tn_lower in name.lower() or name.lower() in tn_lower:
            return info
    return None

