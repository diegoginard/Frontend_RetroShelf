from pathlib import Path
from PySide6.QtCore import Signal, QPoint
from PySide6.QtWidgets import QWidget
from retroshelf.services.controls import (
    matches_action, ACTION_NAV_LETTER, ACTION_NAV_STEP5,
    ACTION_PAGE_UP, ACTION_PAGE_DOWN
)

class BaseLayout(QWidget):
    """
    Clase base abstracta para todos los layouts personalizados de RetroShelf.
    Cualquier layout personalizado debe heredar de esta clase e implementar sus métodos.
    """
    # Señales para comunicar eventos a MainWindow / PlayerWindow
    game_selected = Signal(int)           # Emite game_id cuando se selecciona un juego
    game_activated = Signal(int)          # Emite game_id al hacer doble clic o Enter (ejecutar)
    context_menu_requested = Signal(int, QPoint)  # Emite (game_id, posición_global)
    nav_back_requested = Signal()         # Emite al solicitar volver atrás (Escape, Retroceso o botón B)

    # Identificadores del layout
    LAYOUT_NAME = "Base"
    LAYOUT_DESCRIPTION = "Layout base"

    def __init__(self, parent=None, theme_name: str | None = None, **kwargs):
        super().__init__(parent)
        self.theme_name = theme_name
        self.games = []
        self.current_game_id = None

    def set_games(self, games: list):
        """Recibe la lista de juegos a mostrar (diccionarios de juegos)."""
        self.games = [dict(g) if hasattr(g, "keys") else g for g in games]
        self.render_games()

    def render_games(self):
        """Renderiza los juegos en la interfaz del layout. Debe ser implementado por subclases."""
        raise NotImplementedError

    def select_game_by_id(self, game_id: int):
        """Selecciona visualmente el juego con el ID indicado."""
        self.current_game_id = game_id

    def get_selected_game_id(self) -> int | None:
        """Retorna el ID del juego actualmente seleccionado."""
        return self.current_game_id

    def clear(self):
        """Limpia los elementos del layout."""
        self.games = []
        self.current_game_id = None

    def stop_media(self):
        """Detiene cualquier reproducción multimedia (video, música, efectos) activa en el layout."""
        if hasattr(self, "_want_game_video_playing"):
            self._want_game_video_playing = False
        if hasattr(self, "_want_video_playing"):
            self._want_video_playing = False
        if hasattr(self, "_pending_video_path"):
            self._pending_video_path = None
        for timer_name in ("_video_debounce_timer", "_video_watchdog_timer", "video_timer"):
            if hasattr(self, timer_name):
                try:
                    getattr(self, timer_name).stop()
                except Exception:
                    pass
        for audio_name in ("audio_output", "game_audio", "_audio_output"):
            if hasattr(self, audio_name):
                ao = getattr(self, audio_name)
                if ao:
                    try:
                        ao.setMuted(True)
                        ao.setVolume(0.0)
                    except Exception:
                        pass
        for player_name in ("player", "game_player", "bg_player", "_player"):
            if hasattr(self, player_name):
                p = getattr(self, player_name)
                if p:
                    try:
                        p.stop()
                        from PySide6.QtCore import QUrl
                        p.setSource(QUrl())
                    except Exception:
                        pass
        if hasattr(self, "_current_video_image"):
            self._current_video_image = None
        if hasattr(self, "_game_video_image"):
            self._game_video_image = None
        try:
            self.update()
        except Exception:
            pass

    def set_media_muted(self, muted: bool):
        """Silencia o restaura el audio multimedia del layout."""
        pass

    def jump_to_next_letter(self):
        """
        Salta al primer juego de la siguiente letra en orden alfabético.
        Ej: si el juego actual empieza con 'A', salta al primer juego que empieza con 'B'.
        """
        if not self.games or len(self.games) <= 1:
            return

        def _get_initial(title: str) -> str:
            clean = (title or "").strip().upper()
            for ch in clean:
                if ch.isalnum():
                    return ch if ch.isalpha() else "#"
            return "#"

        n = len(self.games)
        curr_idx = None
        if hasattr(self, "selected_index") and isinstance(self.selected_index, int) and 0 <= self.selected_index < n:
            curr_idx = self.selected_index
        elif self.current_game_id is not None:
            for idx, g in enumerate(self.games):
                if g.get("id") == self.current_game_id:
                    curr_idx = idx
                    break
        elif hasattr(self, "wheel_list") and hasattr(self.wheel_list, "currentRow"):
            row = self.wheel_list.currentRow()
            if 0 <= row < n:
                curr_idx = row
        elif hasattr(self, "table") and hasattr(self.table, "currentRow"):
            row = self.table.currentRow()
            if 0 <= row < n:
                curr_idx = row

        if curr_idx is None:
            curr_idx = 0

        curr_title = self.games[curr_idx].get("title") or self.games[curr_idx].get("rom_name") or ""
        curr_initial = _get_initial(curr_title)

        found_idx = None
        for i in range(1, n):
            target = (curr_idx + i) % n
            title = self.games[target].get("title") or self.games[target].get("rom_name") or ""
            init = _get_initial(title)
            if init != curr_initial:
                found_idx = target
                break

        if found_idx is not None:
            if hasattr(self, "_target_pos") and hasattr(self, "_current_pos"):
                self.selected_index = found_idx
                self._current_pos = float(found_idx - 1)
                self._target_pos = float(found_idx)
                if hasattr(self, "_update_selected_media"):
                    self._update_selected_media(fast_repeat=False)
                elif hasattr(self, "_update_current_selection"):
                    self._update_current_selection()
                if hasattr(self, "_play_nav_sound"):
                    self._play_nav_sound()
                elif hasattr(self, "_play_wheel_sound"):
                    self._play_wheel_sound()
                gid = self.get_selected_game_id()
                if gid:
                    self.game_selected.emit(gid)
                self.update()
            elif hasattr(self, "_wheel_spin_offset"):
                self.selected_index = found_idx
                self._wheel_spin_offset = 2.0
                if hasattr(self, "_wheel_spin_timer") and not self._wheel_spin_timer.isActive():
                    self._wheel_spin_timer.start(16)
                if hasattr(self, "_update_current_selection"):
                    self._update_current_selection()
                if hasattr(self, "_play_wheel_sound"):
                    self._play_wheel_sound()
                gid = self.get_selected_game_id()
                if gid:
                    self.game_selected.emit(gid)
                self.update()
            elif hasattr(self, "_navigate_steps"):
                steps = (found_idx - curr_idx) % n
                self._navigate_steps(steps)
            elif hasattr(self, "wheel_list") and hasattr(self.wheel_list, "setCurrentRow"):
                self.wheel_list.setCurrentRow(found_idx)
            elif hasattr(self, "table") and hasattr(self.table, "selectRow"):
                self.table.selectRow(found_idx)
            else:
                target_gid = self.games[found_idx].get("id")
                if target_gid is not None:
                    self.select_game_by_id(target_gid)
                    self.game_selected.emit(target_gid)

    def navigate_steps(self, steps: int):
        """Avanza o retrocede 'steps' elementos en la lista de juegos (ej: saltar de a 5)."""
        if not self.games:
            return

        if hasattr(self, "_navigate_steps"):
            self._navigate_steps(steps)
        elif hasattr(self, "wheel_list") and hasattr(self.wheel_list, "currentRow"):
            cur = self.wheel_list.currentRow()
            total = self.wheel_list.count()
            if total > 0:
                new_row = max(0, min(total - 1, cur + steps))
                self.wheel_list.setCurrentRow(new_row)
        elif hasattr(self, "table") and hasattr(self.table, "currentRow"):
            cur = self.table.currentRow()
            total = self.table.rowCount()
            if total > 0:
                new_row = max(0, min(total - 1, cur + steps))
                self.table.selectRow(new_row)
        else:
            n = len(self.games)
            curr_idx = 0
            if self.current_game_id is not None:
                for idx, g in enumerate(self.games):
                    if g.get("id") == self.current_game_id:
                        curr_idx = idx
                        break
            new_idx = max(0, min(n - 1, curr_idx + steps))
            target_gid = self.games[new_idx].get("id")
            if target_gid is not None:
                self.select_game_by_id(target_gid)
                self.game_selected.emit(target_gid)

    def keyPressEvent(self, event):
        """Manejo genérico de atajos de salto de letra y saltos de a 5."""
        if matches_action(event, ACTION_NAV_LETTER, getattr(self, "db", None)):
            self.jump_to_next_letter()
            event.accept()
            return
        elif matches_action(event, ACTION_NAV_STEP5, getattr(self, "db", None)):
            self.navigate_steps(5)
            event.accept()
            return
        elif matches_action(event, ACTION_PAGE_UP, getattr(self, "db", None)):
            self.navigate_steps(-5)
            event.accept()
            return
        elif matches_action(event, ACTION_PAGE_DOWN, getattr(self, "db", None)):
            self.navigate_steps(5)
            event.accept()
            return
        super().keyPressEvent(event)
