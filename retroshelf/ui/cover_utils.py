"""
cover_utils.py - Utilidades para carátulas y arte de juegos en RetroShelf.

Provee funciones para cargar imágenes de portada desde disco,
generar portadas generadas proceduralmente cuando no existe imagen,
y gestionar la carpeta de almacenamiento de carátulas.
"""
import hashlib
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QLinearGradient, QFont,
    QBrush, QPainterPath
)
from retroshelf.db import APP_DIR

# Directorio donde se almacenan las carátulas importadas por el usuario
COVERS_DIR = APP_DIR / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

# Paleta de colores vibrantes para portadas generadas
_PALETTE = [
    ("#3d1f8a", "#7b5ce6"),
    ("#1a3a6b", "#3b82f6"),
    ("#1a4a35", "#22c55e"),
    ("#4a1a1a", "#ef4444"),
    ("#4a3a1a", "#f59e0b"),
    ("#1a3a4a", "#06b6d4"),
    ("#3a1a4a", "#a855f7"),
    ("#4a2a1a", "#f97316"),
    ("#1a3a35", "#14b8a6"),
    ("#2a1a4a", "#8b5cf6"),
]

_PLATFORM_ICONS = {
    "super nintendo": "SNES",
    "snes": "SNES",
    "game boy advance": "GBA",
    "gba": "GBA",
    "game boy": "GB",
    "nes": "NES",
    "n64": "N64",
    "nintendo 64": "N64",
    "nds": "NDS",
    "nintendo ds": "NDS",
    "ps1": "PS1",
    "playstation": "PS1",
    "ps2": "PS2",
    "playstation 2": "PS2",
    "psp": "PSP",
    "mega drive": "MD",
    "genesis": "MD",
    "arcade": "ARC",
}


def _get_platform_badge(platform: str | None) -> str:
    if not platform:
        return "ROM"
    pl = platform.lower().strip()
    for key, badge in _PLATFORM_ICONS.items():
        if key in pl:
            return badge
    return platform.upper()[:4]


def _palette_for_title(title: str) -> tuple[str, str]:
    h = int(hashlib.md5(title.encode("utf-8", errors="ignore")).hexdigest(), 16)
    return _PALETTE[h % len(_PALETTE)]


# Public alias so other modules can import it
palette_for_title = _palette_for_title


def generate_placeholder_cover(
    title: str,
    platform: str | None,
    size: QSize = QSize(200, 160)
) -> QPixmap:
    """
    Genera un pixmap de portada procedural con gradiente de color,
    título del juego y badge de plataforma.
    """
    w, h = size.width(), size.height()
    pix = QPixmap(w, h)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    dark_hex, bright_hex = _palette_for_title(title)
    dark_col = QColor(dark_hex)
    bright_col = QColor(bright_hex)

    # Fondo redondeado con gradiente diagonal
    path = QPainterPath()
    path.addRoundedRect(0, 0, w, h, 10, 10)
    painter.setClipPath(path)

    grad = QLinearGradient(0, 0, w, h)
    grad.setColorAt(0.0, dark_col)
    grad.setColorAt(1.0, bright_col.darker(160))
    painter.fillPath(path, QBrush(grad))

    # Highlight sutil en la esquina superior izquierda
    highlight = QLinearGradient(0, 0, w * 0.6, h * 0.6)
    highlight.setColorAt(0.0, QColor(255, 255, 255, 25))
    highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.fillPath(path, QBrush(highlight))

    # Acento inferior vibrante
    accent = QColor(bright_hex)
    accent.setAlpha(200)
    painter.fillRect(0, h - 6, w, 6, accent)

    # Badge de plataforma (arriba a la izquierda)
    badge_text = _get_platform_badge(platform)
    badge_bg = QColor(bright_hex)
    badge_bg.setAlpha(180)
    badge_font = QFont("Segoe UI", max(6, w // 18), QFont.Bold)
    painter.setFont(badge_font)
    fm = painter.fontMetrics()
    bw = fm.horizontalAdvance(badge_text) + 10
    bh = fm.height() + 4
    painter.fillRect(8, 8, bw, bh, badge_bg)
    painter.setPen(QColor(255, 255, 255, 230))
    painter.drawText(QRect(8, 8, bw, bh), Qt.AlignCenter, badge_text)

    # Título centrado
    title_short = title if len(title) <= 28 else title[:26] + "…"
    base_size = max(7, min(13, w // 14))
    title_font = QFont("Segoe UI", base_size, QFont.Bold)
    painter.setFont(title_font)
    painter.setPen(QColor(255, 255, 255, 220))
    text_rect = QRect(8, bh + 12, w - 16, h - bh - 22)
    painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, title_short)

    painter.end()
    return pix


def load_cover(cover_path: str | None, title: str, platform: str | None, size: QSize) -> QPixmap:
    """
    Carga la portada desde disco o genera una procedural si no existe imagen asignada.
    """
    if cover_path:
        p = Path(cover_path)
        if p.exists() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
            pix = QPixmap(str(p))
            if not pix.isNull():
                return pix.scaled(size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    return generate_placeholder_cover(title, platform, size)


def get_cover_save_path(game_id: int, source_ext: str) -> Path:
    """Retorna la ruta donde se debe guardar la carátula importada de un juego."""
    return COVERS_DIR / f"game_{game_id}{source_ext.lower()}"
