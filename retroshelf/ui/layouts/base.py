from pathlib import Path
from PySide6.QtCore import Signal, QPoint
from PySide6.QtWidgets import QWidget

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
        """Recibe la lista de juegos a mostrar (diccionarios o sqlite3.Row)."""
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
        pass

    def set_media_muted(self, muted: bool):
        """Silencia o restaura el audio multimedia del layout."""
        pass
