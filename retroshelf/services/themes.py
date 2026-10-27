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


GENERIC_MEDIA_SPECS: dict[str, list[dict]] = {
    "Grid": [
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": True
        }
    ],
    "Showcase": [
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": True
        },
        {
            "key": "video",
            "label": "Video Snaps",
            "folder": "videos",
            "extensions": [".mp4", ".mkv", ".avi", ".webm"],
            "required": False
        }
    ],
    "Wheel": [
        {
            "key": "wheel",
            "label": "Wheel Logos",
            "folder": "wheel",
            "extensions": [".png", ".webp"],
            "required": True
        },
        {
            "key": "video",
            "label": "Video Snaps",
            "folder": "videos",
            "extensions": [".mp4", ".mkv", ".avi", ".webm"],
            "required": False
        },
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": False
        }
    ],
    "Banners": [
        {
            "key": "wheel",
            "label": "Logos o Banners",
            "folder": "wheel",
            "extensions": [".png", ".webp"],
            "required": True
        },
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": False
        }
    ],
    "Detalles": [
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": True
        }
    ]
}


def get_layout_media_spec(layout_name: str) -> list[dict]:
    """
    Obtiene la especificación de medios requeridos por un layout:
    1. Si es un tema de sistema, busca 'layout.json' en su carpeta.
    2. Si es un layout genérico estándar, retorna su especificación por defecto.
    """
    import json

    if not layout_name:
        return GENERIC_MEDIA_SPECS.get("Wheel", [])

    info = get_theme_info(layout_name)
    if info and info.get("folder"):
        th_folder = Path(info["folder"])
        json_file = th_folder / "layout.json"
        if json_file.is_file():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "media" in data and isinstance(data["media"], list):
                        return data["media"]
            except Exception as e:
                print(f"[RetroShelf] Error al leer {json_file}: {e}")

    # Layouts genéricos estándar
    for name, spec in GENERIC_MEDIA_SPECS.items():
        if layout_name.lower() == name.lower():
            return spec

    # Fallback si no se encontró layout.json ni es genérico conocido
    return [
        {
            "key": "video",
            "label": "Video Snaps",
            "folder": "videos",
            "extensions": [".mp4", ".mkv", ".avi", ".webm"],
            "required": True
        },
        {
            "key": "wheel",
            "label": "Wheel Logos",
            "folder": "wheel",
            "extensions": [".png", ".webp"],
            "required": True
        },
        {
            "key": "cartart",
            "label": "Cartuchos",
            "folder": "cartart",
            "extensions": [".png", ".webp"],
            "required": True
        },
        {
            "key": "boxart",
            "label": "Box Art / Carátulas",
            "folder": "boxart",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": False
        }
    ]


