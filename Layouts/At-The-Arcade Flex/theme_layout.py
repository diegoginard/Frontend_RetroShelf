"""
=============================================================================
Layout Autónomo y Configuración: At-The-Arcade Flex
=============================================================================
Este archivo maneja en su totalidad la configuración, métricas, recursos,
reproducción de video de fondo, video snap en monitor CRT, cartel marquee,
mueble arcade frontal con transparencias, afiche publicitario (flyer) y
ruleta curva interactiva para RetroShelf.
"""
import os
import math
import random
from pathlib import Path
import retroshelf  # Asegura configuración FFmpeg antes de importar QtMultimedia

from PySide6.QtCore import Qt, QSize, QUrl, QRect, QPoint, QTimer, QRectF
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QPixmap, QIcon, QBrush, QPen,
    QFontDatabase, QTransform, QImage
)
from PySide6.QtWidgets import QWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink, QSoundEffect

from retroshelf.ui.layouts.base import BaseLayout
from retroshelf.ui.cover_utils import load_cover
from retroshelf.services.media import find_media_file as cached_find_media_file, resolve_game_media
from retroshelf.services.controls import (
    matches_action, ACTION_NAV_UP, ACTION_NAV_DOWN, ACTION_PAGE_UP,
    ACTION_PAGE_DOWN, ACTION_SELECT, ACTION_MUTE, ACTION_NAV_BACK
)

LAYOUT_DIR = Path(__file__).resolve().parent
COMMON_DIR = LAYOUT_DIR.parent / "gtc-common"


class ThemeLayout(BaseLayout):
    LAYOUT_NAME = "At-The-Arcade Flex"
    LAYOUT_DESCRIPTION = "Layout arcade fotorrealista con mueble interactivo, video de fondo y ruleta"

    CANONICAL_W = 1920
    CANONICAL_H = 1080

    # -------------------------------------------------------------------------
    # REQUERIMIENTOS DE MEDIOS PARA ESTE LAYOUT
    # El usuario selecciona estas carpetas en el Creador de Listas.
    # Al layout no le importa cómo se llamen en el disco, solo su contenido.
    # -------------------------------------------------------------------------
    MEDIA_REQUIREMENTS = [
        {
            "key": "video",
            "label": "Videos",
            "folder": "videos",
            "extensions": [".mp4", ".mkv", ".avi", ".webm"],
            "required": True,
        },
        {
            "key": "wheel",
            "label": "Wheel",
            "folder": "wheel",
            "extensions": [".png", ".webp"],
            "required": True,
        },
        {
            "key": "cabinet",
            "label": "Cabinets",
            "folder": "cabinets",
            "extensions": [".png", ".webp"],
            "required": False,
        },
        {
            "key": "flyer",
            "label": "Flyer",
            "folder": "flyer",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": False,
        },
        {
            "key": "marquee",
            "label": "Marquee",
            "folder": "marquee",
            "extensions": [".png", ".jpg", ".jpeg", ".webp"],
            "required": False,
        },
        {
            "key": "bezel",
            "label": "Bezels",
            "folder": "bezels",
            "extensions": [".png", ".webp"],
            "required": False,
        },
    ]

    # Archivos locales predeterminados del tema
    CABINET_IMAGE = "cabinets.png"
    MARQUEE_IMAGE = "marquee1.jpg"
    BEZEL_IMAGE = "bezels.png"
    POINTER_IMAGE = "pointers/default.png"
    DEFAULT_WHEEL_IMAGE = "wheel.png"

    # Geometría virtual del mueble arcade (1300 x 1080)
    CAB_BASE_W = 1300
    CAB_BASE_H = 1080

    # Coordenadas relativas dentro del mueble
    SNAP_LOCAL_RECT = QRect(200, 318, 706, 526)
    MARQUEE_LOCAL_RECT = QRect(138, 0, 832, 227)

    @staticmethod
    def _resolve_file(rel_path: str | None) -> str | None:
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

    def __init__(self, theme_name: str = "At-The-Arcade Flex", parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.layout_dir = LAYOUT_DIR

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.selected_index = 0
        self.current_media = {}
        self._wheel_pixmaps = {}
        self._art_pix_cache = {}
        self._media_cache = {}
        self._current_marquee_pix: QPixmap | None = None
        self._current_cabinet_pix: QPixmap | None = None
        self._current_bezel_pix: QPixmap | None = None
        self._current_flyer_pix: QPixmap | None = None
        self._pending_video_path: str | None = None

        self._video_debounce_timer = QTimer(self)
        self._video_debounce_timer.setSingleShot(True)
        self._video_debounce_timer.setInterval(160)
        self._video_debounce_timer.timeout.connect(self._play_debounced_video)

        self._video_watchdog_timer = QTimer(self)
        self._video_watchdog_timer.setSingleShot(True)
        self._video_watchdog_timer.setInterval(1200)
        self._video_watchdog_timer.timeout.connect(self._on_game_video_watchdog)

        # Estado del reproductor de video de fondo
        self._bg_video_image: QImage | None = None
        self._bg_player_initialized = False
        self.bg_player = None
        self.bg_sink = None

        # Estado del reproductor de video gameplay
        self._game_video_image: QImage | None = None
        self._game_player_initialized = False
        self._want_game_video_playing = False
        self.game_player = None
        self.game_audio = None
        self.game_sink = None
        self._media_muted = False

        # Animación suave de la ruleta (posición interpolada a 60 FPS)
        self._current_pos = 0.0
        self._target_pos = 0.0
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)  # ~60 FPS
        self._anim_timer.timeout.connect(self._on_animation_tick)
        self._anim_timer.start()

        # Temporizador de desvanecimiento suave de la ruleta (Wheel fadeout tras inactividad)
        self._wheel_alpha = 255.0
        self._target_wheel_alpha = 255.0
        self._wheel_fade_timer = QTimer(self)
        self._wheel_fade_timer.setSingleShot(True)
        self._wheel_fade_timer.setInterval(1400)  # 1.4 segundos de inactividad
        self._wheel_fade_timer.timeout.connect(self._start_wheel_fadeout)

        # Animación del flyer deslizante (aparece 1.5 segundos después de detenerse la ruleta)
        self._flyer_slide = 1.0  # 0.0 = posicionado, 1.0 = fuera de pantalla
        self._flyer_alpha = 255
        self._flyer_ready = False
        self._flyer_delay_timer = QTimer(self)
        self._flyer_delay_timer.setSingleShot(True)
        self._flyer_delay_timer.setInterval(1500)  # 1.5 segundos tras detenerse el carrusel
        self._flyer_delay_timer.timeout.connect(self._on_flyer_delay_timeout)

        # Efectos de sonido
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

        # Precargar imágenes base del tema
        self._pix_cabinet = self._load_pixmap(self._resolve_file(self.CABINET_IMAGE))
        self._pix_marquee_default = self._load_pixmap(self._resolve_file(self.MARQUEE_IMAGE))
        self._current_cabinet_pix = self._pix_cabinet
        self._current_marquee_pix = self._pix_marquee_default
        self._pix_pointer = self._load_pixmap(self._resolve_file(self.POINTER_IMAGE))
        self._pix_wheel_default = self._load_pixmap(self._resolve_file(self.DEFAULT_WHEEL_IMAGE))
        self._pix_scratches = self._load_pixmap(str(COMMON_DIR / "art" / "arcade" / "scratched_cover.png"))
        self._pix_bg_fallback = self._load_pixmap(str(COMMON_DIR / "art" / "arcade" / "bkg.jpg"))

        # Fuentes tipográficas
        self._font_bebas = "Arial"
        self._font_dots = "Arial"
        self._load_fonts()

        # Puntero animado (pulso y oscilación sutil)
        self._pointer_rest_x_ratio = 0.905
        self._pointer_pulse_x_ratio = 0.880
        self._pointer_current_x_ratio = self._pointer_rest_x_ratio
        self._pointer_anim_tick = 0

        # Iniciar video de fondo
        self._init_bg_player()

    def _load_fonts(self):
        f_bebas = LAYOUT_DIR / "BebasNeue Bold.otf"
        if f_bebas.is_file():
            fid = QFontDatabase.addApplicationFont(str(f_bebas))
            if fid != -1:
                fam = QFontDatabase.applicationFontFamilies(fid)
                if fam:
                    self._font_bebas = fam[0]

        f_dots = LAYOUT_DIR / "BigSquareDots.ttf"
        if f_dots.is_file():
            fid2 = QFontDatabase.addApplicationFont(str(f_dots))
            if fid2 != -1:
                fam2 = QFontDatabase.applicationFontFamilies(fid2)
                if fam2:
                    self._font_dots = fam2[0]

    def _load_pixmap(self, path: str | None) -> QPixmap | None:
        if not path or not os.path.isfile(path):
            return None
        pix = QPixmap(path)
        return pix if not pix.isNull() else None

    # -------------------------------------------------------------------------
    # GESTIÓN DE VIDEO DE FONDO Y VIDEO SNAP
    # -------------------------------------------------------------------------
    def _init_bg_player(self):
        if self._bg_player_initialized:
            return
        bg_video_path = COMMON_DIR / "videos" / "bkg_anim.mp4"
        if not bg_video_path.is_file():
            return

        self._bg_player_initialized = True
        self.bg_player = QMediaPlayer(self)
        self.bg_sink = QVideoSink(self)
        self.bg_sink.videoFrameChanged.connect(self._on_bg_frame)
        self.bg_player.setVideoSink(self.bg_sink)
        self.bg_player.setLoops(QMediaPlayer.Infinite)
        self.bg_player.setSource(QUrl.fromLocalFile(str(bg_video_path)))
        self.bg_player.play()

    def _on_bg_frame(self, frame):
        if frame.isValid():
            self._bg_video_image = frame.toImage()
            self.update()

    def _init_game_player(self):
        if self._game_player_initialized and self.game_player is not None:
            return
        self._game_player_initialized = True
        self.game_player = QMediaPlayer(self)
        self.game_audio = QAudioOutput(self)
        self.game_audio.setVolume(0.0 if self._media_muted else 0.8)
        self.game_sink = QVideoSink(self)
        self.game_sink.videoFrameChanged.connect(self._on_game_frame)
        self.game_player.setVideoSink(self.game_sink)
        self.game_player.setAudioOutput(self.game_audio)
        self.game_player.setLoops(QMediaPlayer.Infinite)
        self.game_player.mediaStatusChanged.connect(self._on_game_media_status_changed)
        self.game_player.errorOccurred.connect(self._on_game_player_error)

    def _recreate_game_player(self):
        old_player = self.game_player
        old_audio = self.game_audio
        old_sink = self.game_sink
        self.game_player = None
        self.game_audio = None
        self.game_sink = None
        self._game_player_initialized = False
        if old_sink is not None:
            try:
                old_sink.videoFrameChanged.disconnect()
            except Exception:
                pass
            old_sink.deleteLater()
        if old_player is not None:
            try:
                old_player.mediaStatusChanged.disconnect()
                old_player.errorOccurred.disconnect()
            except Exception:
                pass
            old_player.deleteLater()
        if old_audio is not None:
            old_audio.deleteLater()
        self._init_game_player()

    def _on_game_media_status_changed(self, status):
        if not self.game_player:
            return
        if status in (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.BufferedMedia):
            if self._want_game_video_playing and self.isVisible():
                if self.game_audio:
                    self.game_audio.setMuted(self._media_muted)
                    self.game_audio.setVolume(0.0 if self._media_muted else 0.8)
                if self.game_player.playbackState() != QMediaPlayer.PlayingState:
                    self.game_player.play()
            else:
                if self.game_audio:
                    self.game_audio.setMuted(True)
                    try:
                        self.game_audio.setMuted(True)
                        self.game_audio.setVolume(0.0)
                    except Exception:
                        pass
                if status == QMediaPlayer.BufferedMedia:
                    self.game_player.pause()
        elif status == QMediaPlayer.EndOfMedia:
            if self._want_game_video_playing and self.isVisible():
                self.game_player.setPosition(0)
                self.game_player.play()

    def _on_game_player_error(self, error, error_string=""):
        self._game_video_image = None

    def _on_game_video_watchdog(self):
        if not self._want_game_video_playing or not self._pending_video_path or not self.isVisible():
            return
        if not os.path.isfile(self._pending_video_path) or not self.game_player:
            return
        if self.game_player.mediaStatus() in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia) and self.game_player.playbackState() == QMediaPlayer.PlayingState:
            return
        if self._game_video_image is None or self.game_player.playbackState() != QMediaPlayer.PlayingState:
            try:
                src_url = QUrl.fromLocalFile(self._pending_video_path)
                if self.game_player.source() != src_url:
                    self.game_player.setSource(src_url)
                self.game_player.play()
            except Exception:
                pass

    def _on_game_frame(self, frame):
        if frame.isValid() and self._want_game_video_playing and self.game_player:
            if self._pending_video_path and self.game_player.source() != QUrl.fromLocalFile(self._pending_video_path):
                return
            img = frame.toImage()
            if not img.isNull():
                self._game_video_image = img
                self.update()

    # -------------------------------------------------------------------------
    # RESOLUCIÓN AUTÓNOMA DE MEDIOS DE CADA JUEGO (CON ÍNDICE EN MEMORIA O(1))
    # -------------------------------------------------------------------------
    def _find_media_file(self, folder: str | None, stem: str, exts: tuple[str, ...]) -> str | None:
        return cached_find_media_file(folder, stem, exts)

    def _resolve_game_media(self, game_dict: dict) -> dict:
        gid = game_dict.get("id")
        if gid in self._media_cache:
            return self._media_cache[gid]

        rom_path = game_dict.get("rom_path", "")
        stem = Path(rom_path).stem if rom_path else ""

        # Extensiones de archivos
        img_exts = (".png", ".jpg", ".jpeg", ".webp")
        vid_exts = (".mp4", ".mkv", ".avi", ".webm")

        # 1. Video
        video_file = self._find_media_file(game_dict.get("video_path"), stem, vid_exts)

        # 2. Wheel (Logos)
        wheel_file = self._find_media_file(game_dict.get("wheel_path"), stem, img_exts)

        # 3. Cabinet
        cabinet_file = self._find_media_file(game_dict.get("cabinet_path"), stem, img_exts)

        # 4. Flyer
        flyer_folder = game_dict.get("flyer_path") or game_dict.get("boxart_path")
        flyer_file = self._find_media_file(flyer_folder, stem, img_exts)

        # 5. Marquee
        marquee_file = self._find_media_file(game_dict.get("marquee_path"), stem, img_exts)

        # 6. Bezel (Marco decorativo sobre el monitor)
        bezel_folder = game_dict.get("bezel_path")
        bezel_file = self._find_media_file(bezel_folder, stem, img_exts)
        if not bezel_file and game_dict.get("media_path"):
            mp = Path(game_dict["media_path"])
            for b_cand in ("bezels", "bezel"):
                cand_dir = mp / b_cand
                if cand_dir.is_dir():
                    bezel_file = self._find_media_file(str(cand_dir), stem, img_exts)
                    if bezel_file:
                        break

        res = {
            "video": video_file,
            "wheel": wheel_file,
            "cabinet": cabinet_file,
            "flyer": flyer_file,
            "marquee": marquee_file,
            "bezel": bezel_file,
        }
        if not res["video"] or not res["wheel"] or not res["bezel"]:
            fallback = resolve_game_media(game_dict)
            if not res["video"]:
                res["video"] = fallback.get("video") or fallback.get("snap")
            if not res["wheel"]:
                res["wheel"] = fallback.get("wheel")
            if not res["flyer"]:
                res["flyer"] = fallback.get("boxart")
            if not res["bezel"]:
                res["bezel"] = fallback.get("bezel")
        self._media_cache[gid] = res
        return res

    # -------------------------------------------------------------------------
    # INTERFAZ BASELAYOUT
    # -------------------------------------------------------------------------
    def set_games(self, games: list[dict]):
        self.games = games or []
        self._media_cache.clear()
        self._wheel_pixmaps.clear()
        self.selected_index = 0
        self._current_pos = 0.0
        self._target_pos = 0.0
        self._update_selected_media()
        self.update()

    def select_game_by_id(self, game_id: int):
        for idx, g in enumerate(self.games):
            if g.get("id") == game_id:
                self.selected_index = idx
                self._target_pos = float(idx)
                self._update_selected_media()
                self._reset_wheel_fade()
                self.update()
                break

    def get_selected_game_id(self) -> int | None:
        if self.games and 0 <= self.selected_index < len(self.games):
            return self.games[self.selected_index].get("id")
        return None

    def set_media_muted(self, muted: bool):
        self._media_muted = muted
        if self.game_audio:
            self.game_audio.setVolume(0.0 if muted else 0.8)

    def stop_media(self):
        self._want_game_video_playing = False
        self._video_debounce_timer.stop()
        self._video_watchdog_timer.stop()
        if self.game_audio:
            self.game_audio.setVolume(0.0)
        if self.game_player and self.game_player.mediaStatus() == QMediaPlayer.BufferedMedia:
            try:
                self.game_player.pause()
            except Exception:
                pass
        self._game_video_image = None
        self.update()

    # -------------------------------------------------------------------------
    # NAVEGACIÓN Y ANIMACIÓN
    # -------------------------------------------------------------------------
    def _navigate_steps(self, steps: int, fast_repeat: bool = False):
        if not self.games:
            return
        n = len(self.games)
        new_idx = (self.selected_index + steps) % n
        self.selected_index = new_idx
        self._target_pos += steps
        self._flyer_ready = False
        self._flyer_slide = 1.0  # Ocultar el flyer mientras se mueve la ruleta
        self._current_flyer_pix = None
        self._flyer_delay_timer.start(1500)
        self._pointer_current_x_ratio = self._pointer_pulse_x_ratio
        self._reset_wheel_fade()
        self._play_nav_sound()
        self._update_selected_media(fast_repeat=fast_repeat)
        gid = self.get_selected_game_id()
        if gid:
            self.game_selected.emit(gid)
        self.update()

    def _on_flyer_delay_timeout(self):
        if not self.games or not (0 <= self.selected_index < len(self.games)):
            return
        flyer_file = self.current_media.get("flyer")
        self._current_flyer_pix = self._get_cached_art_pixmap(flyer_file) if flyer_file else None
        if self._current_flyer_pix is not None:
            self._flyer_ready = True
            self.update()

    def _play_nav_sound(self):
        try:
            if self._sound_effect and self._sound_effect.isLoaded():
                self._sound_effect.play()
        except Exception:
            pass

    def _play_select_sound(self):
        try:
            if self._select_sound_effect and self._select_sound_effect.isLoaded():
                self._select_sound_effect.play()
        except Exception:
            pass

    def _start_wheel_fadeout(self):
        self._target_wheel_alpha = 0.0

    def _reset_wheel_fade(self):
        self._wheel_alpha = 255.0
        self._target_wheel_alpha = 255.0
        self._wheel_fade_timer.start()

    def _on_animation_tick(self):
        needs_update = False

        # 1. Interpolación de la ruleta
        diff = self._target_pos - self._current_pos
        if abs(diff) > 0.005:
            self._current_pos += diff * 0.28
            needs_update = True
            # Mientras el carrusel de wheels sigue girando, reiniciar los 1.5 segundos del flyer
            self._flyer_ready = False
            self._flyer_slide = 1.0
            self._flyer_delay_timer.start(1200)
        else:
            if self._current_pos != self._target_pos:
                self._current_pos = self._target_pos
                self._flyer_delay_timer.start(1000)

        # 2. Desvanecimiento suave de la ruleta (Wheel fadeout)
        a_diff = self._target_wheel_alpha - self._wheel_alpha
        if abs(a_diff) > 1.0:
            self._wheel_alpha += a_diff * 0.10
            needs_update = True
        else:
            self._wheel_alpha = self._target_wheel_alpha

        # 3. Deslizamiento suave del flyer (solo tras cumplirse los 2s desde que se detuvo el carrusel)
        if self._flyer_ready and self._current_flyer_pix is not None:
            if self._flyer_slide > 0.005:
                self._flyer_slide += (0.0 - self._flyer_slide) * 0.15
                needs_update = True
            elif self._flyer_slide != 0.0:
                self._flyer_slide = 0.0
                needs_update = True

        # 4. Pulso suave del puntero al cambiar de juego
        self._pointer_anim_tick += 1
        p_diff = self._pointer_rest_x_ratio - self._pointer_current_x_ratio
        if abs(p_diff) > 0.001:
            self._pointer_current_x_ratio += p_diff * 0.22
            needs_update = True
        else:
            self._pointer_current_x_ratio = self._pointer_rest_x_ratio

        if needs_update:
            self.update()

    def _get_cached_art_pixmap(self, path: str | None) -> QPixmap | None:
        if not path:
            return None
        if path in self._art_pix_cache:
            return self._art_pix_cache[path]
        pix = self._load_pixmap(path)
        if len(self._art_pix_cache) >= 120:
            self._art_pix_cache.pop(next(iter(self._art_pix_cache)), None)
        self._art_pix_cache[path] = pix
        return pix

    def _load_current_game_art(self):
        custom_cab_file = self.current_media.get("cabinet")
        custom_cab_pix = self._get_cached_art_pixmap(custom_cab_file) if custom_cab_file else None
        has_custom_cab = custom_cab_pix is not None
        self._current_cabinet_pix = custom_cab_pix if has_custom_cab else self._pix_cabinet

        marq_file = self.current_media.get("marquee")
        marq_pix = self._get_cached_art_pixmap(marq_file) if marq_file else None
        if marq_pix is not None:
            self._current_marquee_pix = marq_pix
        else:
            self._current_marquee_pix = None if has_custom_cab else self._pix_marquee_default

        bezel_file = self.current_media.get("bezel")
        self._current_bezel_pix = self._get_cached_art_pixmap(bezel_file) if bezel_file else None

    def _update_selected_media(self, fast_repeat: bool = False):
        self._flyer_ready = False
        self._flyer_slide = 1.0
        self._current_flyer_pix = None
        self._flyer_delay_timer.start(1500)

        if not self.games or not (0 <= self.selected_index < len(self.games)):
            self.current_media = {}
            self._current_marquee_pix = self._pix_marquee_default
            self._current_cabinet_pix = self._pix_cabinet
            self._current_bezel_pix = None
            self._pending_video_path = None
            self._want_game_video_playing = False
            self._video_debounce_timer.stop()
            self._video_watchdog_timer.stop()
            self._flyer_delay_timer.stop()
            if self.game_audio:
                self.game_audio.setVolume(0.0)
            self._game_video_image = None
            return

        current_game = self.games[self.selected_index]
        self.current_media = self._resolve_game_media(current_game)

        # Si se cambia de juego normalmente, cargar cabinet y marquee al instante;
        # si se mantiene presionado recorriendo rápido la ruleta, diferir lectura de disco al detenerse
        if not fast_repeat:
            self._load_current_game_art()
        else:
            custom_cab_file = self.current_media.get("cabinet")
            if custom_cab_file and custom_cab_file in self._art_pix_cache:
                self._load_current_game_art()
            elif not custom_cab_file:
                self._load_current_game_art()

        # Reproducir video snap con debounce suave para no bloquear al girar rápido la ruleta
        self._pending_video_path = self.current_media.get("video")
        self._want_game_video_playing = False
        self._video_watchdog_timer.stop()
        if self.game_audio:
            try:
                self.game_audio.setMuted(True)
                self.game_audio.setVolume(0.0)
            except Exception:
                pass
        if self.game_player:
            try:
                self.game_player.pause()
            except Exception:
                pass
        self._game_video_image = None
        self._video_debounce_timer.start()

    def _play_debounced_video(self):
        if not self.isVisible():
            return
        self._load_current_game_art()
        self.update()
        video_path = self._pending_video_path
        if video_path and os.path.isfile(video_path):
            self._init_game_player()
            if self.game_player:
                self._want_game_video_playing = True
                if self.game_audio:
                    self.game_audio.setMuted(self._media_muted)
                    self.game_audio.setVolume(0.0 if self._media_muted else 0.8)
                try:
                    src_url = QUrl.fromLocalFile(video_path)
                    if self.game_player.source() == src_url:
                        self.game_player.setPosition(0)
                    else:
                        self.game_player.setSource(src_url)
                    self.game_player.play()
                    self._video_watchdog_timer.start()
                except Exception:
                    pass
        else:
            self._want_game_video_playing = False
            if self.game_audio:
                try:
                    self.game_audio.setMuted(True)
                    self.game_audio.setVolume(0.0)
                except Exception:
                    pass
            if self.game_player:
                try:
                    self.game_player.stop()
                    self.game_player.setSource(QUrl())
                except Exception:
                    pass
            self._game_video_image = None
            self.update()

    # -------------------------------------------------------------------------
    # RENDERIZADO VISUAL A 60 FPS
    # -------------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # 1. FONDO DE VIDEO O IMAGEN ESTÁTICA
        if self._bg_video_image:
            painter.drawImage(QRect(0, 0, w, h), self._bg_video_image)
        elif self._pix_bg_fallback:
            if not hasattr(self, "_cached_bg_pix") or getattr(self, "_cached_bg_size", None) != (w, h):
                self._cached_bg_pix = self._pix_bg_fallback.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self._cached_bg_size = (w, h)
            painter.drawPixmap(0, 0, self._cached_bg_pix)
        else:
            painter.fillRect(QRect(0, 0, w, h), QColor(10, 8, 16))

        # Calcular geometría responsiva del mueble arcade (escala a la altura)
        cab_h = h
        cab_w = int(cab_h * (self.CAB_BASE_W / float(self.CAB_BASE_H)))
        # Limitar ancho del mueble solo si la parte visible (1070/1300) supera el 68% del ancho (w * 0.82)
        if cab_w > int(w * 0.82):
            cab_w = int(w * 0.82)
        cab_x = 0
        cab_y = 0

        scale_x = cab_w / float(self.CAB_BASE_W)
        scale_y = cab_h / float(self.CAB_BASE_H)

        # Rectángulos de pantalla monitor y cartel marquee escalados
        snap_rect = QRect(
            cab_x + int(self.SNAP_LOCAL_RECT.x() * scale_x),
            cab_y + int(self.SNAP_LOCAL_RECT.y() * scale_y),
            int(self.SNAP_LOCAL_RECT.width() * scale_x),
            int(self.SNAP_LOCAL_RECT.height() * scale_y)
        )
        marquee_rect = QRect(
            cab_x + int(self.MARQUEE_LOCAL_RECT.x() * scale_x),
            cab_y + int(self.MARQUEE_LOCAL_RECT.y() * scale_y),
            int(self.MARQUEE_LOCAL_RECT.width() * scale_x),
            int(self.MARQUEE_LOCAL_RECT.height() * scale_y)
        )

        # 2. MONITOR CRT (Capa trasera del monitor)
        painter.fillRect(snap_rect, QColor(0, 0, 0))
        if self._game_video_image:
            vw, vh = self._game_video_image.width(), self._game_video_image.height()
            s = min(snap_rect.width() / vw, snap_rect.height() / vh) if vw > 0 and vh > 0 else 1.0
            dw, dh = int(vw * s), int(vh * s)
            vx = snap_rect.x() + (snap_rect.width() - dw) // 2
            vy = snap_rect.y() + (snap_rect.height() - dh) // 2
            painter.drawImage(QRect(vx, vy, dw, dh), self._game_video_image)
        else:
            f_pix = self._current_flyer_pix
            if f_pix:
                pw, ph = f_pix.width(), f_pix.height()
                s = min(snap_rect.width() / pw, snap_rect.height() / ph) if pw > 0 and ph > 0 else 1.0
                dw, dh = int(pw * s), int(ph * s)
                cx = snap_rect.x() + (snap_rect.width() - dw) // 2
                cy = snap_rect.y() + (snap_rect.height() - dh) // 2
                painter.drawPixmap(QRect(cx, cy, dw, dh), f_pix)
            else:
                f_ph = QFont(self._font_dots, max(12, int(h * 0.024)), QFont.Bold)
                painter.setFont(f_ph)
                painter.setPen(QColor(80, 80, 95))
                painter.drawText(snap_rect, Qt.AlignCenter, "INSERT COIN\nNO VIDEO SNAP")

        # Capa de Bezel del juego (encima del video snap en el monitor CRT)
        if self._current_bezel_pix:
            painter.drawPixmap(snap_rect, self._current_bezel_pix)

        # Capa de reflejo / vidrio rayado CRT sobre el monitor
        if self._pix_scratches:
            s_size = (snap_rect.width(), snap_rect.height())
            if not hasattr(self, "_cached_scratches_pix") or getattr(self, "_cached_scratches_size", None) != s_size:
                self._cached_scratches_pix = self._pix_scratches.scaled(snap_rect.width(), snap_rect.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self._cached_scratches_size = s_size
            painter.setOpacity(0.40)
            painter.drawPixmap(snap_rect.x(), snap_rect.y(), self._cached_scratches_pix)
            painter.setOpacity(1.0)

        # 3. MARQUEE (Capa trasera de la marquesina)
        pix_marq = self._current_marquee_pix
        if pix_marq:
            marq_key = (id(pix_marq), marquee_rect.width(), marquee_rect.height())
            if not hasattr(self, "_cached_marq_pix") or getattr(self, "_cached_marq_key", None) != marq_key:
                self._cached_marq_pix = pix_marq.scaled(marquee_rect.width(), marquee_rect.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self._cached_marq_key = marq_key
            painter.drawPixmap(marquee_rect.x(), marquee_rect.y(), self._cached_marq_pix)
            painter.fillRect(marquee_rect, QColor(255, 255, 255, 25))

        # 4. MUEBLE ARCADE FRONTAL (Capa frontal con huecos transparentes)
        pix_cab = self._current_cabinet_pix or self._pix_cabinet
        if pix_cab:
            cab_key = (id(pix_cab), cab_w, cab_h)
            if not hasattr(self, "_cached_cab_pix") or getattr(self, "_cached_cab_key", None) != cab_key:
                self._cached_cab_pix = pix_cab.scaled(cab_w, cab_h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self._cached_cab_key = cab_key
            painter.drawPixmap(cab_x, cab_y, self._cached_cab_pix)

        # 5. FLYER DEL JUEGO (Lado derecho de la pantalla)
        self._draw_flyer(painter, w, h)

        # 6. RULETA CURVA (WHEEL CONVEYOR)
        if self._wheel_alpha > 2.0:
            painter.setOpacity(self._wheel_alpha / 255.0)
            self._draw_wheel(painter, w, h)
            painter.setOpacity(1.0)

        # 7. BARRA INFERIOR / INFORMACIÓN DE JUEGO
        self._draw_footer(painter, w, h)

    def _draw_flyer(self, painter: QPainter, w: int, h: int):
        if not self._flyer_ready:
            return
        pix = self._current_flyer_pix
        if not pix:
            return

        # Flyer 30% más grande que el tamaño original (0.22 * 1.30 y 0.52 * 1.30)
        target_w = int(w * 0.22 * 1.30)
        target_h = int(h * 0.52 * 1.30)
        target_x = int(w * 0.67) + int(self._flyer_slide * (w * 0.35))
        target_y = int(h * 0.26)

        flyer_rect = QRect(target_x, target_y, target_w, target_h)

        pw, ph = pix.width(), pix.height()
        s = min(target_w / pw, target_h / ph) if pw > 0 and ph > 0 else 1.0
        dw, dh = int(pw * s), int(ph * s)
        ax = flyer_rect.x() + (flyer_rect.width() - dw) // 2
        ay = flyer_rect.y() + (flyer_rect.height() - dh) // 2
        painter.drawPixmap(QRect(ax, ay, dw, dh), pix)

    def _draw_wheel(self, painter: QPainter, w: int, h: int):
        if not self.games:
            return

        n = len(self.games)
        total_slots = 11
        half_slots = total_slots // 2

        # Puntero central (anclado al borde derecho de la pantalla, apuntando hacia la ruleta)
        if self._pix_pointer:
            ptr_size = max(24, int(h * 0.16))
            ptr_y = (h - ptr_size) // 2
            visible_w = int(ptr_size * 0.56)
            edge_margin = max(4, int(w * 0.003))
            pulse_offset = int(w * (self._pointer_rest_x_ratio - self._pointer_current_x_ratio))
            idle_oscillation = int(w * (math.sin(self._pointer_anim_tick * 0.08) * 0.002))
            ptr_x = w - edge_margin - visible_w - pulse_offset + idle_oscillation
            painter.drawPixmap(ptr_x, ptr_y, ptr_size, ptr_size, self._pix_pointer)

        # Dibujar cada slot a lo largo del arco elíptico
        for offset in range(-half_slots, half_slots + 1):
            slot_idx = int(round(self._current_pos)) + offset
            game_idx = slot_idx % n
            game = self.games[game_idx]

            # Distancia continua al centro
            dist = (slot_idx - self._current_pos)
            if abs(dist) > half_slots + 0.5:
                continue

            # Curvatura elíptica
            angle = (dist / float(half_slots + 1)) * (math.pi * 0.42)
            curv_x = math.cos(angle)
            curv_y = math.sin(angle)

            # Posición en pantalla
            center_x = int(w * 0.85) - int(curv_x * (w * 0.12))
            center_y = int(h * 0.50) + int(curv_y * (h * 0.45))

            # Escala destacada para el ítem central
            is_center = abs(dist) < 0.5
            slot_scale = 1.0 - (abs(dist) * 0.10)
            if is_center:
                slot_w = int(w * 0.22 * 1.25)
                slot_h = int(h * 0.12 * 1.25)
                alpha = 255
            else:
                slot_w = int(w * 0.18 * slot_scale)
                slot_h = int(h * 0.09 * slot_scale)
                alpha = max(60, int(220 - abs(dist) * 35))

            logo_rect = QRect(center_x - slot_w // 2, center_y - slot_h // 2, slot_w, slot_h)

            # Cargar imagen de wheel del juego
            pix_logo = self._get_wheel_pixmap(game)

            if pix_logo:
                painter.setOpacity((alpha / 255.0) * (self._wheel_alpha / 255.0))
                pw, ph = pix_logo.width(), pix_logo.height()
                s = min(logo_rect.width() / pw, logo_rect.height() / ph) if pw > 0 and ph > 0 else 1.0
                dw, dh = int(pw * s), int(ph * s)
                lx = logo_rect.x() + (logo_rect.width() - dw) // 2
                ly = logo_rect.y() + (logo_rect.height() - dh) // 2
                painter.drawPixmap(QRect(lx, ly, dw, dh), pix_logo)
                painter.setOpacity(self._wheel_alpha / 255.0)

    def _create_text_wheel_pixmap(self, title: str) -> QPixmap:
        """Crea un logotipo tipográfico estilizado en memoria y lo cachea para no recalcular texto cada frame."""
        pix = QPixmap(400, 160)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing, True)
        f_title = QFont(self._font_bebas, 24, QFont.Bold)
        p.setFont(f_title)
        p.setPen(QColor(240, 240, 240))
        p.drawText(pix.rect(), Qt.AlignCenter | Qt.TextWordWrap, (title or "Arcade Game").upper())
        p.end()
        return pix

    def _get_wheel_pixmap(self, game: dict) -> QPixmap | None:
        gid = game.get("id")
        if gid in self._wheel_pixmaps:
            return self._wheel_pixmaps[gid]

        media = self._resolve_game_media(game)
        w_file = media.get("wheel")
        pix = self._load_pixmap(w_file)
        if pix and (pix.width() > 480 or pix.height() > 240):
            pix = pix.scaled(480, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not pix:
            title = game.get("title") or "Arcade Game"
            pix = self._create_text_wheel_pixmap(title)
        self._wheel_pixmaps[gid] = pix
        return pix

    def _draw_footer(self, painter: QPainter, w: int, h: int):
        bar_h = max(26, int(h * 0.042))
        bar_y = h - bar_h

        # Franja negra translúcida
        painter.fillRect(QRect(0, bar_y, w, bar_h), QColor(8, 6, 12, 225))

        if not self.games or not (0 <= self.selected_index < len(self.games)):
            return

        current_game = self.games[self.selected_index]
        title = current_game.get("title") or "Desconocido"

        f_size = max(11, int(h * 0.024))
        f_title = QFont(self._font_bebas, f_size, QFont.Bold)
        f_title.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
        painter.setFont(f_title)
        painter.setPen(QColor(255, 255, 255))
        title_rect = QRect(int(w * 0.04), bar_y, int(w * 0.65), bar_h)
        painter.drawText(title_rect, Qt.AlignVCenter | Qt.AlignLeft, title.upper())

        counter_text = f"ARCADE: {self.selected_index + 1} / {len(self.games)}"
        f_counter = QFont(self._font_dots, max(10, int(h * 0.020)), QFont.Bold)
        painter.setFont(f_counter)
        painter.setPen(QColor(245, 185, 35))
        counter_rect = QRect(int(w * 0.70), bar_y, int(w * 0.26), bar_h)
        painter.drawText(counter_rect, Qt.AlignVCenter | Qt.AlignRight, counter_text)

    # -------------------------------------------------------------------------
    # CONTROL DE EVENTOS DE TECLADO Y RATÓN
    # -------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        fast = event.isAutoRepeat()
        if matches_action(event, ACTION_NAV_UP):
            self._navigate_steps(-1, fast_repeat=fast)
            event.accept()
        elif matches_action(event, ACTION_NAV_DOWN):
            self._navigate_steps(1, fast_repeat=fast)
            event.accept()
        elif matches_action(event, ACTION_PAGE_UP):
            self._navigate_steps(-5, fast_repeat=fast)
            event.accept()
        elif matches_action(event, ACTION_PAGE_DOWN):
            self._navigate_steps(5, fast_repeat=fast)
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
        elif matches_action(event, ACTION_MUTE) or key == Qt.Key_M:
            self.set_media_muted(not self._media_muted)
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._navigate_steps(-1)
        elif delta < 0:
            self._navigate_steps(1)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Si se hace click cerca del monitor, activar el juego
            cab_h = self.height()
            cab_w = int(cab_h * (self.CAB_BASE_W / float(self.CAB_BASE_H)))
            scale_x = cab_w / float(self.CAB_BASE_W)
            scale_y = cab_h / float(self.CAB_BASE_H)
            snap_rect = QRect(
                int(self.SNAP_LOCAL_RECT.x() * scale_x),
                int(self.SNAP_LOCAL_RECT.y() * scale_y),
                int(self.SNAP_LOCAL_RECT.width() * scale_x),
                int(self.SNAP_LOCAL_RECT.height() * scale_y)
            )
            if snap_rect.contains(event.pos()):
                gid = self.get_selected_game_id()
                if gid:
                    self._play_select_sound()
                    self.game_activated.emit(gid)
                event.accept()
                return

            # Clics arriba o abajo para navegar
            if event.y() < self.height() * 0.40:
                self._navigate_steps(-1)
            elif event.y() > self.height() * 0.60:
                self._navigate_steps(1)
            else:
                gid = self.get_selected_game_id()
                if gid:
                    self._play_select_sound()
                    self.game_activated.emit(gid)
            event.accept()
