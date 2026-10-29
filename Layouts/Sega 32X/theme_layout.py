import retroshelf
"""
=============================================================================
Layout Autónomo y Configuración: Sega 32X
=============================================================================
Este archivo maneja en su totalidad la configuración, métricas, recursos,
reproducción de video, animaciones de entrada, inserción de cartucho y renderizado
completo del sistema Sega 32X para RetroShelf.
"""
import os
import math
import random
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QUrl, QRect, QPoint, QTimer, QRectF
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QPixmap, QIcon, QBrush, QPen,
    QFontDatabase, QTransform, QImage
)
from PySide6.QtWidgets import QWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink, QSoundEffect

from retroshelf.ui.layouts.base import BaseLayout
from retroshelf.services.media import resolve_game_media
from retroshelf.ui.cover_utils import load_cover
from retroshelf.services.controls import (
    matches_action, ACTION_NAV_UP, ACTION_NAV_DOWN, ACTION_PAGE_UP,
    ACTION_PAGE_DOWN, ACTION_SELECT, ACTION_MUTE, ACTION_NAV_BACK
)

LAYOUT_DIR = Path(__file__).resolve().parent
COMMON_DIR = LAYOUT_DIR.parent / "gtc-common"


class ThemeLayout(BaseLayout):
    LAYOUT_NAME = "Sega 32X"
    LAYOUT_DESCRIPTION = "Layout temático de Sega 32X fiel a Attract-Mode con TV CRT y cartucho insertándose"

    CANONICAL_W = 1920
    CANONICAL_H = 1080

    # -------------------------------------------------------------------------
    # REQUERIMIENTOS DE MEDIOS PARA ESTE LAYOUT (LEÍDOS DIRECTAMENTE POR EL SISTEMA)
    # -------------------------------------------------------------------------
    MEDIA_REQUIREMENTS = [
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
        }
    ]

    # -------------------------------------------------------------------------
    # ASIGNACIÓN DE ARCHIVOS PROPIOS DEL LAYOUT (ADMINISTRADOS POR ESTE ARCHIVO)
    # -------------------------------------------------------------------------
    BKG_IMAGE = "bg.jpeg"
    TV_IMAGE = "tv.png"
    CONSOLE_IMAGE = "console.png"
    CONSOLE_COVER_IMAGE = "console_cover.png"
    JOYSTICK_IMAGE = None
    AVATAR_IMAGE = "avatar.png"
    LOGO_IMAGE = "logo.png"
    CARTART_IMAGE = "cartart.png"
    BOXART_IMAGE = None
    WHEEL_IMAGE = "wheel.png"
    POINTER_IMAGE = "pointers/default.png"
    FONT_FILES = [
        "Handel Gothic BT.ttf",
        "BebasNeue Bold.otf",
    ]

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN GEOMÉTRICA DE SEGA 32X
    # -------------------------------------------------------------------------
    # TV Snap Video: (x, y, w, h) en ratios de pantalla (1920x1080)
    TV_RECT = (0.044, 0.235, 0.315, 0.433)

    # Cartucho insertándose desde arriba hacia la ranura del 32X
    CART_RECT = (0.329, 0.480, 0.100, 0.180)
    CART_END_Y = 0.480
    IS_CD = False

    # Avatar del sistema (F-14 Tomcat)
    AVATAR_SCALE = 1.0
    AVATAR_X = 0.0
    AVATAR_Y = 0.0

    # Logotipo del sistema
    LOGO_SCALE = 1.0

    # Carátula (Boxart) anclada abajo a la izquierda
    BOXART_X = 0.450
    BOXART_W = 0.240
    BOXART_H = 0.380
    BOXART_BOTTOM_Y = 0.928
    BOXART_ANCHOR = "bottom"

    # Curva interactiva de la ruleta (Conveyor Wheel de 14 nodos interpolados a 60 FPS)
    CONVEYOR_X = [0.89, 0.85, 0.83, 0.80, 0.77, 0.74, 0.71, 0.625, 0.71, 0.74, 0.77, 0.80, 0.83, 0.89]
    CONVEYOR_Y = [-0.34, -0.22, -0.105, 0.00, 0.105, 0.215, 0.325, 0.421, 0.59, 0.70, 0.81, 0.915, 0.99, 1.12]
    CONVEYOR_W = [0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.30, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18]
    CONVEYOR_H = [0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.186, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10]
    CONVEYOR_R = [35.0, 30.0, 25.0, 20.0, 15.0, 10.0, 5.0, 0.0, -10.0, -15.0, -20.0, -25.0, -30.0, -35.0]
    CONVEYOR_A = [0, 20, 35, 60, 90, 125, 160, 255, 160, 125, 90, 60, 35, 0]

    @classmethod
    def _resolve_file(cls, rel_path: str | None) -> str | None:
        """Resuelve una ruta relativa dentro de la carpeta propia del layout."""
        if not rel_path:
            return None
        p = LAYOUT_DIR / rel_path
        if p.is_file():
            return str(p)
        cand = LAYOUT_DIR / Path(rel_path).name
        if cand.is_file():
            return str(cand)
        cand_ptr = LAYOUT_DIR / "pointers" / Path(rel_path).name
        if cand_ptr.is_file():
            return str(cand_ptr)
        return None

    def __init__(self, theme_name: str = "Sega 32X", parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.layout_dir = LAYOUT_DIR

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.selected_index = 0
        self.current_media = {}
        self._wheel_pixmaps = {}
        self._current_box_pixmap = None
        self._current_cart_pixmap = None

        self._player_initialized = False
        self.player = None
        self.audio_output = None
        self.video_sink = None
        self._media_muted = False
        self.db = None
        self._current_video_image: QImage | None = None

        # Efectos de sonido directos desde gtc-common
        self._sound_effect = QSoundEffect(self)
        self._sound_effect.setVolume(0.4)
        click_sound = COMMON_DIR / "sounds" / "joystick.mp3"
        if click_sound.is_file():
            self._sound_effect.setSource(QUrl.fromLocalFile(str(click_sound)))

        self._select_sound_effect = QSoundEffect(self)
        self._select_sound_effect.setVolume(0.5)
        sel_sound = COMMON_DIR / "sounds" / "Mame_coin.mp3"
        if sel_sound.is_file():
            self._select_sound_effect.setSource(QUrl.fromLocalFile(str(sel_sound)))

        # Precargar imágenes asignadas directamente en este layout
        self._pix_bkg = self._load_pixmap(self._resolve_file(self.BKG_IMAGE))
        self._pix_tv = self._load_pixmap(self._resolve_file(self.TV_IMAGE))
        self._pix_console = self._load_pixmap(self._resolve_file(self.CONSOLE_IMAGE))
        self._pix_console_cover = self._load_pixmap(self._resolve_file(self.CONSOLE_COVER_IMAGE))
        self._pix_joystick = self._load_pixmap(self._resolve_file(self.JOYSTICK_IMAGE))
        self._pix_avatar = self._load_pixmap(self._resolve_file(self.AVATAR_IMAGE))
        self._pix_logo = self._load_pixmap(self._resolve_file(self.LOGO_IMAGE))
        self._pix_cartart_frame = self._load_pixmap(self._resolve_file(self.CARTART_IMAGE))
        self._pix_boxart_frame = self._load_pixmap(self._resolve_file(self.BOXART_IMAGE))

        # Recursos compartidos directos desde gtc-common (sin diccionarios)
        self._pix_scanlines = self._load_pixmap(str(COMMON_DIR / "art" / "scanlines_1920.png"))
        self._pix_wheel_art = self._load_pixmap(str(COMMON_DIR / "art" / "wheel_art.png"))
        self._pix_frame = self._load_pixmap(str(COMMON_DIR / "art" / "frame.png"))
        static_vid = COMMON_DIR / "videos" / "static.mp4"
        self._static_video_path = str(static_vid) if static_vid.is_file() else None

        # Sombra de ruleta directa desde gtc-common/wheel
        shadow_file = COMMON_DIR / "wheel" / "wheel_shadow.png"
        if not shadow_file.is_file():
            shadow_file = COMMON_DIR / "wheels" / "wheel_shadow.png"
        self._pix_wheel_shadow = self._load_pixmap(str(shadow_file)) if shadow_file.is_file() else None

        # Puntero animado de la ruleta asignado en este layout
        pointer_path = self._resolve_file(self.POINTER_IMAGE)
        self._pix_pointer = self._load_pixmap(pointer_path)

        # Diccionario theme_info autogenerado internamente por el layout
        self.theme_info = {
            "name": self.theme_name,
            "folder": str(LAYOUT_DIR),
            "bkg": self._resolve_file(self.BKG_IMAGE),
            "tv": self._resolve_file(self.TV_IMAGE),
            "console": self._resolve_file(self.CONSOLE_IMAGE),
            "console_cover": self._resolve_file(self.CONSOLE_COVER_IMAGE),
            "joystick": self._resolve_file(self.JOYSTICK_IMAGE),
            "avatar": self._resolve_file(self.AVATAR_IMAGE),
            "character": self._resolve_file(self.AVATAR_IMAGE),
            "logo": self._resolve_file(self.LOGO_IMAGE),
            "cartart": self._resolve_file(self.CARTART_IMAGE),
            "boxart": self._resolve_file(self.BOXART_IMAGE),
            "wheel": self._resolve_file(self.WHEEL_IMAGE),
            "pointer": pointer_path,
        }

        self._pointer_rest_x_ratio = 0.905
        self._pointer_pulse_x_ratio = 0.880
        self._pointer_current_x_ratio = self._pointer_rest_x_ratio
        self._pointer_anim_tick = 0

        self._pointer_anim_timer = QTimer(self)
        self._pointer_anim_timer.timeout.connect(self._on_pointer_tick)
        if self._pix_pointer:
            self._pointer_anim_timer.start(16)

        # Tipografías
        self._font_handel = "sans-serif"
        self._font_bebas = "sans-serif"
        self._load_theme_fonts()

        # Animación de giro suave de la ruleta
        self._wheel_spin_offset = 0.0
        self._wheel_spin_timer = QTimer(self)
        self._wheel_spin_timer.timeout.connect(self._on_wheel_spin_tick)

        # Animación de avatar
        self._avatar_anim_time = 0.0
        self._avatar_offset_x = 0.0
        self._avatar_offset_y = 0.0
        self._avatar_bounce_timer = QTimer(self)
        self._avatar_bounce_timer.timeout.connect(self._on_avatar_bounce_tick)
        self._avatar_bounce_timer.start(20)

        # Animación de cartucho cayendo desde arriba
        self._cart_anim_timer = QTimer(self)
        self._cart_anim_timer.timeout.connect(self._on_cart_anim_tick)
        self._cart_anim_elapsed = 0
        self._cart_anim_duration = 700
        self._cart_start_y_ratio = -0.45
        self._cart_end_y_ratio = self.CART_END_Y
        self._cart_current_y_ratio = self._cart_end_y_ratio

        # Animación de caída del logo superior
        self._logo_anim_timer = QTimer(self)
        self._logo_anim_timer.timeout.connect(self._on_logo_anim_tick)
        self._logo_anim_elapsed = 0
        self._logo_anim_duration = 1200
        self._logo_current_y_offset_ratio = 0.0

        # Animación de entrada de la carátula (boxart)
        self._boxart_anim_timer = QTimer(self)
        self._boxart_anim_timer.timeout.connect(self._on_boxart_anim_tick)
        self._boxart_anim_elapsed = 0
        self._boxart_anim_duration = 450
        self._boxart_current_x_offset_ratio = 0.0
        self._boxart_alpha = 1.0

        self._start_logo_animation()

    def _load_pixmap(self, path: str | None) -> QPixmap | None:
        if path and os.path.isfile(path):
            pix = QPixmap(path)
            return pix if not pix.isNull() else None
        return None

    def _load_theme_fonts(self):
        font_paths = []
        for f_rel in getattr(self, "FONT_FILES", []):
            resolved = self._resolve_file(f_rel)
            if resolved:
                font_paths.append(resolved)
        if not font_paths:
            for f in LAYOUT_DIR.iterdir():
                if f.is_file() and f.suffix.lower() in (".ttf", ".otf"):
                    font_paths.append(str(f))

        for f_path in font_paths:
            if os.path.isfile(f_path):
                fid = QFontDatabase.addApplicationFont(f_path)
                if fid != -1:
                    families = QFontDatabase.applicationFontFamilies(fid)
                    if families:
                        fname = os.path.basename(f_path).lower()
                        if "nise" in fname or "genesis" in fname or "handel" in fname:
                            self._font_handel = families[0]
                        elif "bebas" in fname:
                            self._font_bebas = families[0]
                        else:
                            self._font_handel = families[0]

    def _play_wheel_sound(self):
        try:
            if self._sound_effect.source().isValid():
                self._sound_effect.play()
            else:
                c_sound = COMMON_DIR / "sounds" / "joystick.mp3"
                if c_sound.is_file():
                    self._sound_effect.setSource(QUrl.fromLocalFile(str(c_sound)))
                    self._sound_effect.play()
        except Exception:
            pass

    def _play_select_sound(self):
        try:
            if self._select_sound_effect.source().isValid():
                self._select_sound_effect.play()
            else:
                sel_sound = COMMON_DIR / "sounds" / "Mame_coin.mp3"
                if sel_sound.is_file():
                    self._select_sound_effect.setSource(QUrl.fromLocalFile(str(sel_sound)))
                    self._select_sound_effect.play()
        except Exception:
            pass

    def _on_pointer_tick(self):
        self._pointer_anim_tick += 1
        diff = self._pointer_rest_x_ratio - self._pointer_current_x_ratio
        if abs(diff) > 0.0005:
            self._pointer_current_x_ratio += diff * 0.20
            self.update()
        else:
            self._pointer_current_x_ratio = self._pointer_rest_x_ratio
            if self._pointer_anim_tick % 2 == 0:
                self.update()

    def _on_avatar_bounce_tick(self):
        self._avatar_anim_time += 0.04
        t = self._avatar_anim_time
        self._avatar_offset_x = math.sin(t * 0.9) * 8.0
        self._avatar_offset_y = (math.sin(t * 1.8) * 10.0)
        if self._pix_avatar:
            self.update()

    def _navigate_steps(self, delta_steps: int):
        n = len(self.games)
        if n == 0 or delta_steps == 0:
            return

        self.selected_index = (self.selected_index + delta_steps) % n
        self._wheel_spin_offset += float(delta_steps)
        self._wheel_spin_offset = max(-5.0, min(5.0, self._wheel_spin_offset))
        self._pointer_current_x_ratio = self._pointer_pulse_x_ratio

        self._play_wheel_sound()
        self._update_current_selection()
        if not self._wheel_spin_timer.isActive():
            self._wheel_spin_timer.start(16)
        self.update()

    def _on_wheel_spin_tick(self):
        self._wheel_spin_offset *= 0.72
        if abs(self._wheel_spin_offset) < 0.015:
            self._wheel_spin_offset = 0.0
            self._wheel_spin_timer.stop()
        self.update()

    def _on_cart_anim_tick(self):
        dt = 16
        self._cart_anim_elapsed += dt
        t = min(self._cart_anim_elapsed / self._cart_anim_duration, 1.0)
        ease = 1.0 - (1.0 - t) ** 3
        self._cart_current_y_ratio = (
            self._cart_start_y_ratio
            + (self._cart_end_y_ratio - self._cart_start_y_ratio) * ease
        )
        self.update()
        if t >= 1.0:
            self._cart_anim_timer.stop()
            self._cart_current_y_ratio = self._cart_end_y_ratio

    def _start_cart_animation(self):
        self._cart_anim_elapsed = 0
        self._cart_current_y_ratio = self._cart_start_y_ratio
        self._cart_anim_timer.start(16)

    def _on_logo_anim_tick(self):
        dt = 16
        self._logo_anim_elapsed += dt
        t = min(self._logo_anim_elapsed / self._logo_anim_duration, 1.0)
        p = 0.3
        s = p / 4.0
        if t == 0.0:
            ease = 0.0
        elif t >= 1.0:
            ease = 1.0
        else:
            ease = math.pow(2.0, -10.0 * t) * math.sin((t - s) * (2.0 * math.pi) / p) + 1.0

        start_offset = -0.50
        self._logo_current_y_offset_ratio = start_offset * (1.0 - ease)
        self.update()
        if t >= 1.0:
            self._logo_anim_timer.stop()
            self._logo_current_y_offset_ratio = 0.0

    def _start_logo_animation(self):
        self._logo_anim_elapsed = 0
        self._logo_current_y_offset_ratio = -1.5
        self._logo_anim_timer.start(16)

    def _on_boxart_anim_tick(self):
        dt = 16
        self._boxart_anim_elapsed += dt
        t = min(self._boxart_anim_elapsed / self._boxart_duration, 1.0)
        ease = 1.0 - (1.0 - t) ** 3
        start_x_offset = -0.5
        self._boxart_current_x_offset_ratio = start_x_offset * (1.0 - ease)
        self._boxart_alpha = min(1.0, max(0.0, ease))
        self.update()
        if t >= 1.0:
            self._boxart_anim_timer.stop()
            self._boxart_current_x_offset_ratio = 0.0
            self._boxart_alpha = 1.0

    def _start_boxart_animation(self):
        self._boxart_anim_elapsed = 0
        self._boxart_duration = 450
        self._boxart_current_x_offset_ratio = -0.5
        self._boxart_alpha = 0.0
        self._boxart_anim_timer.start(16)

    def _init_player(self):
        if self._player_initialized:
            return
        self._player_initialized = True
        self._want_video_playing = False
        self._pending_video_path = None
        self._pending_video_is_snap = False
        self._video_debounce_timer = QTimer(self)
        self._video_debounce_timer.setSingleShot(True)
        self._video_debounce_timer.setInterval(160)
        self._video_debounce_timer.timeout.connect(self._play_debounced_video)

        self._video_watchdog_timer = QTimer(self)
        self._video_watchdog_timer.setSingleShot(True)
        self._video_watchdog_timer.setInterval(1200)
        self._video_watchdog_timer.timeout.connect(self._on_video_watchdog)

        self.player = QMediaPlayer(self)
        self.player.setLoops(QMediaPlayer.Infinite)
        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(0.7)
        self.player.setAudioOutput(self.audio_output)
        self.video_sink = QVideoSink(self)
        self.video_sink.videoFrameChanged.connect(self._on_video_frame_changed)
        self.player.setVideoSink(self.video_sink)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_player_error)

    def _on_media_status_changed(self, status):
        if not self.player:
            return
        if status in (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.BufferedMedia):
            if getattr(self, "_want_video_playing", False) and self.isVisible():
                if self.audio_output:
                    is_snap = getattr(self, "_pending_video_is_snap", True)
                    self.audio_output.setVolume(0.7 if is_snap else 0.0)
                    if getattr(self, "_media_muted", False):
                        self.audio_output.setMuted(True)
                if self.player.playbackState() != QMediaPlayer.PlayingState:
                    self.player.play()
            else:
                if self.audio_output:
                    try:
                        self.audio_output.setMuted(True)
                        self.audio_output.setVolume(0.0)
                    except Exception:
                        pass
                if status == QMediaPlayer.BufferedMedia:
                    self.player.pause()
        elif status == QMediaPlayer.EndOfMedia:
            if getattr(self, "_want_video_playing", False) and self.isVisible():
                self.player.setPosition(0)
                self.player.play()

    def _on_player_error(self, error, error_string=""):
        self._current_video_image = None

    def _on_video_watchdog(self):
        if not getattr(self, "_want_video_playing", False) or not getattr(self, "_pending_video_path", None) or not self.isVisible():
            return
        if not os.path.isfile(self._pending_video_path) or not self.player:
            return
        if self.player.mediaStatus() == QMediaPlayer.LoadingMedia:
            return
        if self._current_video_image is None or self.player.playbackState() != QMediaPlayer.PlayingState:
            try:
                src_url = QUrl.fromLocalFile(self._pending_video_path)
                if self.player.source() != src_url:
                    self.player.setSource(src_url)
                self.player.play()
            except Exception:
                pass

    def _on_video_frame_changed(self, frame):
        if frame.isValid() and getattr(self, "_want_video_playing", True) and self.player:
            p_path = getattr(self, "_pending_video_path", None)
            if p_path and self.player.source() != QUrl.fromLocalFile(p_path):
                return
            img = frame.toImage()
            if not img.isNull():
                self._current_video_image = img
                self.update()

    def stop_media(self):
        self._want_video_playing = False
        self._pending_video_path = None
        if hasattr(self, '_video_debounce_timer'):
            self._video_debounce_timer.stop()
        if hasattr(self, '_video_watchdog_timer'):
            self._video_watchdog_timer.stop()
        if hasattr(self, 'audio_output') and self.audio_output:
            try:
                self.audio_output.setMuted(True)
                self.audio_output.setVolume(0.0)
            except Exception:
                pass
        if hasattr(self, 'player') and self.player:
            try:
                self.player.stop()
                self.player.setSource(QUrl())
            except Exception:
                pass
        self._current_video_image = None
        self.update()

    def set_db(self, db):
        self.db = db
        if self.games and 0 <= self.selected_index < len(self.games):
            self._load_game_media(self.games[self.selected_index])

    def set_games(self, games: list):
        super().set_games(games)
        self.selected_index = 0
        self._wheel_pixmaps.clear()
        if self.games:
            self._load_game_media(self.games[0])
            self._start_cart_animation()
            self._start_boxart_animation()
            self._start_logo_animation()
        else:
            self.current_media = {}
            self._current_box_pixmap = None
            self._current_cart_pixmap = None
            if self.player:
                self.player.stop()
            self._current_video_image = None
        self.update()

    def render_games(self):
        self.update()

    def select_game_by_id(self, game_id: int):
        for idx, g in enumerate(self.games):
            if g.get("id") == game_id:
                if self.selected_index != idx:
                    self.selected_index = idx
                    self._update_current_selection()
                    self.update()
                break

    def get_selected_game_id(self) -> int | None:
        if self.games and 0 <= self.selected_index < len(self.games):
            return self.games[self.selected_index].get("id")
        return None

    def _update_current_selection(self):
        if not self.games or not (0 <= self.selected_index < len(self.games)):
            return
        current_game = self.games[self.selected_index]
        self.current_game_id = current_game.get("id")
        self.game_selected.emit(self.current_game_id)
        self._load_game_media(current_game)
        self._start_cart_animation()
        self._start_boxart_animation()

    def _load_game_media(self, game: dict):
        gid = game.get("id")
        if self.db and gid:
            self.current_media = resolve_game_media(self.db, gid, game)
        else:
            self.current_media = {
                "boxart": game.get("cover_path") or game.get("boxart_path"),
                "cartart": game.get("cartart_path"),
                "snap": game.get("video_path") or game.get("snap_path"),
                "wheel": game.get("wheel_path") or game.get("logo_path"),
            }
        if not hasattr(self, "_art_pix_cache"):
            self._art_pix_cache = {}
        box_file = self.current_media.get("boxart")
        if not box_file and game.get("cover_path"):
            box_file = game["cover_path"]
        self._pending_box_file = box_file
        self._current_box_pixmap = self._art_pix_cache.get(box_file) if box_file else None

        cart_file = self.current_media.get("cartart")
        self._pending_cart_file = cart_file
        self._current_cart_pixmap = self._art_pix_cache.get(cart_file) if cart_file else None

        self._play_current_video()

    def _load_pending_art(self):
        if not hasattr(self, "_art_pix_cache"):
            self._art_pix_cache = {}
        if len(self._art_pix_cache) > 80:
            self._art_pix_cache.clear()
        b_file = getattr(self, "_pending_box_file", None)
        if b_file:
            if b_file not in self._art_pix_cache:
                p = QPixmap(b_file) if os.path.isfile(b_file) else QPixmap()
                self._art_pix_cache[b_file] = p if not p.isNull() else None
            self._current_box_pixmap = self._art_pix_cache[b_file]
        else:
            self._current_box_pixmap = None

        c_file = getattr(self, "_pending_cart_file", None)
        if c_file:
            if c_file not in self._art_pix_cache:
                p = QPixmap(c_file) if os.path.isfile(c_file) else QPixmap()
                self._art_pix_cache[c_file] = p if not p.isNull() else None
            self._current_cart_pixmap = self._art_pix_cache[c_file]
        else:
            self._current_cart_pixmap = None

    def _play_current_video(self):
        self._init_player()
        video_file = self.current_media.get("snap")
        target_file = None
        is_snap = False

        if video_file and os.path.isfile(video_file):
            target_file = video_file
            is_snap = True
        elif self._static_video_path and os.path.isfile(self._static_video_path):
            target_file = self._static_video_path
            is_snap = False

        self._pending_video_path = target_file
        self._pending_video_is_snap = is_snap
        self._want_video_playing = False
        self._video_watchdog_timer.stop()
        if self.audio_output:
            self.audio_output.setVolume(0.0)
        if self.player and self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
            try:
                self.player.pause()
            except Exception:
                pass
        self._current_video_image = None
        self._video_debounce_timer.start()

    def _play_debounced_video(self):
        if not self.isVisible():
            return
        self._load_pending_art()
        self.update()
        target_file = getattr(self, "_pending_video_path", None)
        is_snap = getattr(self, "_pending_video_is_snap", False)
        if target_file and os.path.isfile(target_file):
            self._want_video_playing = True
            if self.audio_output:
                self.audio_output.setVolume(0.7 if is_snap else 0.0)
                if getattr(self, "_media_muted", False):
                    self.audio_output.setMuted(True)
            try:
                src_url = QUrl.fromLocalFile(target_file)
                if self.player.source() == src_url:
                    self.player.setPosition(0)
                else:
                    self.player.setSource(src_url)
                self.player.play()
                self._video_watchdog_timer.start()
            except Exception:
                pass
        else:
            self._want_video_playing = False
            if self.audio_output:
                try:
                    self.audio_output.setMuted(True)
                    self.audio_output.setVolume(0.0)
                except Exception:
                    pass
            if self.player:
                try:
                    self.player.stop()
                    self.player.setSource(QUrl())
                except Exception:
                    pass
            self._current_video_image = None
            self.update()

    def _get_game_wheel_pixmap(self, game: dict) -> QPixmap | None:
        gid = game.get("id")
        if gid in self._wheel_pixmaps:
            return self._wheel_pixmaps[gid]

        wheel_path = None
        media = resolve_game_media(game)
        if media.get("wheel"):
            wheel_path = media["wheel"]
        elif game.get("wheel_path") and os.path.isfile(game.get("wheel_path")):
            wheel_path = game["wheel_path"]

        if wheel_path and os.path.isfile(wheel_path):
            p = QPixmap(wheel_path)
            if not p.isNull():
                self._wheel_pixmaps[gid] = p
                return p

        self._wheel_pixmaps[gid] = None
        return None

    def _get_scaled_canvas(self) -> QRect:
        w = self.width()
        h = self.height()
        target_aspect = self.CANONICAL_W / self.CANONICAL_H
        current_aspect = w / max(h, 1)

        if current_aspect > target_aspect:
            sh = h
            sw = int(h * target_aspect)
            sx = (w - sw) // 2
            sy = 0
        else:
            sw = w
            sh = int(w / target_aspect)
            sx = 0
            sy = (h - sh) // 2

        return QRect(sx, sy, sw, sh)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        try:
            painter.fillRect(self.rect(), QColor(0, 0, 0))
            sr = self._get_scaled_canvas()
            sw = sr.width()
            sh = sr.height()
            sx = sr.x()
            sy = sr.y()

            # Capa 1: Fondo escénico
            if self._pix_bkg:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_bkg)
            else:
                painter.fillRect(sr, QColor(10, 10, 18))

            # Capa 2: Snap Video o estática dentro de la pantalla CRT
            tv_rx, tv_ry, tv_rw, tv_rh = self.TV_RECT
            tv_snap_x = sx + int(sw * tv_rx)
            tv_snap_y = sy + int(sh * tv_ry)
            tv_snap_w = int(sw * tv_rw)
            tv_snap_h = int(sh * tv_rh)

            painter.save()
            painter.fillRect(tv_snap_x, tv_snap_y, tv_snap_w, tv_snap_h, QColor(0, 0, 0))
            if self._current_video_image:
                pix = QPixmap.fromImage(self._current_video_image)
                painter.drawPixmap(tv_snap_x, tv_snap_y, tv_snap_w, tv_snap_h, pix)
            painter.restore()

            # Capa 3: Scanlines CRT
            if self._pix_scanlines:
                painter.save()
                painter.setOpacity(0.35)
                painter.drawPixmap(tv_snap_x, tv_snap_y, tv_snap_w, tv_snap_h, self._pix_scanlines)
                painter.restore()

            # Capa 4: Marco de la TV
            if self._pix_tv:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_tv)

            # Capa 5: Logotipo oficial de Sega 32X
            self._draw_logo(painter, sr)

            # Capa 6: Avatar del sistema
            self._draw_avatar(painter, sr)
           
            # Capa 7: Consola Sega 32X
            if self._pix_console:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_console)

            # Capa 8: Cartucho insertándose desde arriba
            self._draw_cart_or_disc(painter, sr)

            # Capa 9: Tapa frontal si existe
            if self._pix_console_cover:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_console_cover)

            # Capa 10: Joystick si existe
            if self._pix_joystick:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_joystick)

            # Capa 11: Carátula del juego (Boxart)
            self._draw_boxart(painter, sr)

            # Capa 12: Sombra / fondo de la ruleta
            if self._pix_wheel_shadow:
                painter.drawPixmap(sx, sy, sw, sh, self._pix_wheel_shadow)

            # Capa 13: Ruleta curva interactiva
            if self.games:
                self._draw_wheel_conveyor(painter, sr)

            # Capa 14: Puntero selector de la ruleta (fiel a Attract-Mode, apunta desde la derecha)
            self._draw_pointer(painter, sr)

            # Capa 15: Barra inferior con título
            self._draw_bottom_bar(painter, sr)

        finally:
            painter.end()

    def _draw_avatar(self, painter: QPainter, sr: QRect):
        avatar_pix = self._pix_avatar
        if not avatar_pix:
            return
        sw, sh = sr.width(), sr.height()
        sx, sy = sr.x(), sr.y()
        scale = getattr(self, "AVATAR_SCALE", 1.0)
        aw = int(sw * scale)
        ah = int(sh * scale)
        pos_x = int(getattr(self, "AVATAR_X", 0.0) * sw)
        pos_y = int(getattr(self, "AVATAR_Y", 0.0) * sh)
        anim_x = int(self._avatar_offset_x * (sw / self.CANONICAL_W))
        anim_y = int(self._avatar_offset_y * (sh / self.CANONICAL_H))
        draw_x = sx + pos_x + anim_x
        draw_y = sy + pos_y + anim_y
        painter.drawPixmap(draw_x, draw_y, aw, ah, avatar_pix)

    def _draw_logo(self, painter: QPainter, sr: QRect):
        if not self._pix_logo:
            return
        sw, sh = sr.width(), sr.height()
        sx, sy = sr.x(), sr.y()
        logo_y = sy + int(sh * self._logo_current_y_offset_ratio)
        if self.LOGO_SCALE != 1.0:
            lw = int(sw * self.LOGO_SCALE)
            lh = int(sh * self.LOGO_SCALE)
            painter.drawPixmap(sx, logo_y, lw, lh, self._pix_logo)
        else:
            painter.drawPixmap(sx, logo_y, sw, sh, self._pix_logo)

    def _draw_cart_or_disc(self, painter: QPainter, sr: QRect):
        sw, sh = sr.width(), sr.height()
        sx, sy = sr.x(), sr.y()

        cx, cy_ratio, cw, ch = self.CART_RECT
        cart_x = sx + int(sw * cx)
        cart_w = int(sw * cw)
        cart_h = int(sh * ch)
        cart_y = sy + int(sh * self._cart_current_y_ratio)

        cart_pix = getattr(self, "_current_cart_pixmap", None) or self._pix_cartart_frame
        if cart_pix and not cart_pix.isNull():
            painter.save()
            pw = cart_pix.width()
            ph = cart_pix.height()
            s = min(cart_w / pw, cart_h / ph) if pw > 0 and ph > 0 else 1.0
            dw = int(pw * s)
            dh = int(ph * s)
            draw_cx = cart_x + (cart_w - dw) // 2
            draw_cy = cart_y + (cart_h - dh) // 2
            painter.drawPixmap(QRect(draw_cx, draw_cy, dw, dh), cart_pix)
            painter.restore()

    def _draw_boxart(self, painter: QPainter, sr: QRect):
        sw = sr.width()
        sh = sr.height()
        sx = sr.x()
        sy = sr.y()

        box_w = int(sw * self.BOXART_W)
        box_h = int(sh * self.BOXART_H)
        box_x = sx + int(sw * self.BOXART_X)

        box_pix = getattr(self, "_current_box_pixmap", None) or self._pix_boxart_frame
        if box_pix and not box_pix.isNull():
            pw = box_pix.width()
            ph = box_pix.height()
            s = min(box_w / pw, box_h / ph) if pw > 0 and ph > 0 else 1.0
            dw = int(pw * s)
            dh = int(ph * s)

            box_x_offset = int(sw * self._boxart_current_x_offset_ratio)
            draw_x = box_x + (box_w - dw) // 2 + box_x_offset
            bottom_y = sy + int(sh * self.BOXART_BOTTOM_Y)
            draw_y = bottom_y - dh
            painter.save()
            painter.setOpacity(self._boxart_alpha)
            painter.drawPixmap(QRect(draw_x, draw_y, dw, dh), box_pix)
            painter.restore()

    def _draw_wheel_conveyor(self, painter: QPainter, sr: QRect):
        sw = sr.width()
        sh = sr.height()
        sx = sr.x()
        sy = sr.y()

        n_games = len(self.games)
        if n_games == 0:
            return

        draw_offsets = [-6, 6, -5, 5, -4, 4, -3, 3, -2, 2, -1, 1, 0]

        for offset in draw_offsets:
            game_idx = (self.selected_index + offset) % n_games
            game = self.games[game_idx]

            pos = (7.0 + offset) + self._wheel_spin_offset
            if pos < 0.0 or pos >= 13.0:
                continue

            i0 = int(math.floor(pos))
            i1 = min(i0 + 1, 13)
            p = pos - i0

            rx = self.CONVEYOR_X[i0] + p * (self.CONVEYOR_X[i1] - self.CONVEYOR_X[i0])
            ry = self.CONVEYOR_Y[i0] + p * (self.CONVEYOR_Y[i1] - self.CONVEYOR_Y[i0])
            rw = self.CONVEYOR_W[i0] + p * (self.CONVEYOR_W[i1] - self.CONVEYOR_W[i0])
            rh = self.CONVEYOR_H[i0] + p * (self.CONVEYOR_H[i1] - self.CONVEYOR_H[i0])
            angle = self.CONVEYOR_R[i0] + p * (self.CONVEYOR_R[i1] - self.CONVEYOR_R[i0])
            alpha = int(self.CONVEYOR_A[i0] + p * (self.CONVEYOR_A[i1] - self.CONVEYOR_A[i0]))

            if alpha <= 0:
                continue

            dist_from_center = abs(pos - 7.0)
            is_selected = (dist_from_center < 0.5)

            item_w = int(sw * rw)
            item_h = int(sh * rh)
            item_cx = sx + int(sw * rx) + item_w // 2
            item_cy = sy + int(sh * ry) + item_h // 2

            painter.save()
            try:
                painter.translate(item_cx, item_cy)
                if angle != 0:
                    painter.rotate(angle)

                painter.setOpacity(min(1.0, max(0.0, alpha / 255.0)))
                rect = QRect(-item_w // 2, -item_h // 2, item_w, item_h)
                wheel_pix = self._get_game_wheel_pixmap(game)

                if wheel_pix and not wheel_pix.isNull():
                    pw = wheel_pix.width()
                    ph = wheel_pix.height()
                    max_w = item_w - 12
                    max_h = item_h - 8
                    s = min(max_w / pw, max_h / ph) if pw > 0 and ph > 0 else 1.0
                    dw = int(pw * s)
                    dh = int(ph * s)
                    painter.drawPixmap(QRect(-dw // 2, -dh // 2, dw, dh), wheel_pix)
                else:
                    card_path = QPainterPath()
                    card_path.addRoundedRect(rect, 8, 8)
                    bg_col = QColor(135, 50, 219, 210) if is_selected else QColor(25, 28, 45, 180)
                    border_col = QColor(255, 255, 255, 220) if is_selected else QColor(70, 80, 110, 120)
                    painter.fillPath(card_path, bg_col)
                    painter.setPen(QPen(border_col, 2 if is_selected else 1))
                    painter.drawPath(card_path)

                    title = game.get("title") or "Juego"
                    painter.setPen(QColor(255, 255, 255))
                    f_size = max(11, int(item_h * 0.32))
                    f = QFont(self._font_handel, f_size, QFont.Bold)
                    painter.setFont(f)
                    painter.drawText(rect.adjusted(8, 4, -8, -4), Qt.AlignCenter | Qt.TextWordWrap, title)
            finally:
                painter.restore()

    def _draw_pointer(self, painter: QPainter, sr: QRect):
        if not self._pix_pointer or not self.games:
            return

        sw = sr.width()
        sh = sr.height()
        sx = sr.x()
        sy = sr.y()

        ptr_size = int(sh * 0.24)
        ptr_w = ptr_size
        ptr_h = ptr_size

        # Alineación vertical exacta con el centro del slot seleccionado de la ruleta (índice 7)
        slot_center_y_ratio = self.CONVEYOR_Y[7] + (self.CONVEYOR_H[7] / 2.0)
        ptr_cy = sy + int(sh * slot_center_y_ratio)
        ptr_y = ptr_cy - (ptr_h // 2)

        # Ancho visible del puntero (~56% del ancho de 326)
        visible_w = int(ptr_w * 0.56)
        # Casi pegado al borde derecho de la pantalla (margen mínimo de ~4px)
        edge_margin = max(4, int(sw * 0.003))
        base_x = sx + sw - edge_margin - visible_w

        # Pulso elástico al cambiar de juego + micro oscilación en reposo
        pulse_offset = int(sw * (self._pointer_rest_x_ratio - self._pointer_current_x_ratio))
        idle_oscillation = int(sw * (math.sin(self._pointer_anim_tick * 0.08) * 0.002))
        ptr_x = base_x - pulse_offset + idle_oscillation

        painter.save()
        painter.setOpacity(1.0)
        painter.drawPixmap(ptr_x, ptr_y, ptr_w, ptr_h, self._pix_pointer)
        painter.restore()

    def _draw_bottom_bar(self, painter: QPainter, sr: QRect):
        sw = sr.width()
        sh = sr.height()
        sx = sr.x()
        sy = sr.y()

        bar_h = int(sh * 0.075)
        bar_y = sy + sh - bar_h

        if self._pix_frame:
            painter.drawPixmap(sx, bar_y, sw, bar_h, self._pix_frame)
        else:
            painter.fillRect(QRect(sx, bar_y, sw, bar_h), QColor(8, 10, 20, 235))

        if not self.games or not (0 <= self.selected_index < len(self.games)):
            return

        current_game = self.games[self.selected_index]
        title = current_game.get("title") or "Desconocido"

        f_size = max(13, int(sh * 0.032))
        f_title = QFont(self._font_bebas, f_size, QFont.Bold)
        f_title.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(f_title)
        painter.setPen(QColor(255, 255, 255))
        title_rect = QRect(sx + int(sw * 0.08), bar_y, int(sw * 0.65), bar_h)
        painter.drawText(title_rect, Qt.AlignVCenter | Qt.AlignLeft, title.upper())

        counter_text = f"GAME: {self.selected_index + 1} / {len(self.games)}"
        f_counter = QFont(self._font_handel, max(11, int(sh * 0.024)), QFont.Bold)
        painter.setFont(f_counter)
        painter.setPen(QColor(180, 210, 255))
        counter_rect = QRect(sx + int(sw * 0.70), bar_y, int(sw * 0.25), bar_h)
        painter.drawText(counter_rect, Qt.AlignVCenter | Qt.AlignRight, counter_text)

    def keyPressEvent(self, event):
        key = event.key()
        if matches_action(event, ACTION_NAV_UP):
            self._navigate_steps(-1)
            event.accept()
        elif matches_action(event, ACTION_NAV_DOWN):
            self._navigate_steps(1)
            event.accept()
        elif matches_action(event, ACTION_PAGE_UP):
            self._navigate_steps(-5)
            event.accept()
        elif matches_action(event, ACTION_PAGE_DOWN):
            self._navigate_steps(5)
            event.accept()
        elif matches_action(event, ACTION_SELECT) or key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            gid = self.get_selected_game_id()
            if gid:
                self._play_select_sound()
                self.game_activated.emit(gid)
            event.accept()
        elif matches_action(event, ACTION_NAV_BACK):
            self.nav_back_requested.emit()
            event.accept()
        elif matches_action(event, ACTION_MUTE):
            self.set_media_muted(not getattr(self, "_media_muted", False))
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle > 0:
            self._navigate_steps(-1)
        elif angle < 0:
            self._navigate_steps(1)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            gid = self.get_selected_game_id()
            if gid:
                self.context_menu_requested.emit(gid, event.globalPosition().toPoint())
            event.accept()
            return
        elif event.button() == Qt.LeftButton:
            sr = self._get_scaled_canvas()
            pos_y = event.position().y()
            if pos_y < sr.y() + sr.height() * 0.45:
                self._navigate_steps(-1)
            elif pos_y > sr.y() + sr.height() * 0.55:
                self._navigate_steps(1)
            else:
                gid = self.get_selected_game_id()
                if gid:
                    self._play_select_sound()
                    self.game_activated.emit(gid)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            gid = self.get_selected_game_id()
            if gid:
                self._play_select_sound()
                self.game_activated.emit(gid)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def set_media_muted(self, muted: bool):
        self._media_muted = muted
        if self.audio_output:
            try:
                self.audio_output.setMuted(muted)
            except Exception:
                pass

    def stop_media(self):
        self._want_video_playing = False
        self._pending_video_path = None
        if hasattr(self, '_video_debounce_timer'):
            self._video_debounce_timer.stop()
        if hasattr(self, '_video_watchdog_timer'):
            self._video_watchdog_timer.stop()
        if hasattr(self, 'audio_output') and self.audio_output:
            try:
                self.audio_output.setMuted(True)
                self.audio_output.setVolume(0.0)
            except Exception:
                pass
        if hasattr(self, 'player') and self.player:
            try:
                self.player.stop()
                self.player.setSource(QUrl())
            except Exception:
                pass
        self._current_video_image = None
        self.update()

    def hideEvent(self, event):
        self.stop_media()
        super().hideEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self._start_logo_animation()

    def clear(self):
        self._wheel_spin_offset = 0.0
        if hasattr(self, '_wheel_spin_timer') and self._wheel_spin_timer.isActive():
            self._wheel_spin_timer.stop()
        self._current_video_image = None
        self.stop_media()
        super().clear()
        self._wheel_pixmaps.clear()


# Alias compatible
SystemThemeLayout = ThemeLayout
