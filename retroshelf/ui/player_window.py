import sys
import subprocess
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QStackedWidget, QFrame, QScrollArea
)
from retroshelf.db import Database
from retroshelf.services.launcher import launch_game
from retroshelf.ui.layouts import LAYOUT_REGISTRY, get_available_layouts, create_layout, resolve_theme_name

PLAYER_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #12141a;
    color: #e6e9f2;
}
QScrollArea {
    border: none;
    background: transparent;
}
QPushButton[class="platform-btn"], QPushButton.platform-btn {
    background-color: #1b1f2b;
    border: 1px solid #282f42;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 10pt;
    font-weight: 600;
    color: #a3b1c6;
}
QPushButton[class="platform-btn"]:hover, QPushButton.platform-btn:hover {
    background-color: #262c3e;
    border-color: #434f6e;
    color: #ffffff;
}
QPushButton[class="platform-btn"]:checked, QPushButton.platform-btn:checked {
    background-color: #5d48d9;
    border-color: #7866ed;
    color: #ffffff;
}
QLineEdit {
    background-color: #1b1e2a;
    border: 1px solid #2b3244;
    border-radius: 8px;
    padding: 8px 14px;
    color: #f1f3f9;
    font-size: 10pt;
}
QLineEdit:focus {
    border-color: #5d48d9;
}
QPushButton[class="action-icon"], QPushButton.action-icon {
    background-color: #1b1e2a;
    border: 1px solid #2b3244;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 9pt;
    font-weight: 500;
}
QPushButton[class="action-icon"]:hover, QPushButton.action-icon:hover {
    background-color: #292f42;
    border-color: #3f4963;
}
"""

class PlayerWindow(QMainWindow):
    """
    Ventana del Reproductor / Frontend de Juegos.
    Modo visual limpio, enfocado 100% en la experiencia de juego.
    No muestra opciones de configuración, edición de archivos ni diálogos técnicos.
    """
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_list_id = None
        self.current_game_id = None
        self.games_cache = []
        self.platform_buttons = []
        self.navigation_history = []

        self.setWindowTitle("RetroShelf — Frontend")
        self.resize(1280, 800)
        self.setMinimumSize(800, 480)
        self.setStyleSheet(PLAYER_STYLESHEET)

        self._build_ui()
        self._setup_shortcuts()
        self.load_lists()

    def _build_ui(self):
        root = QWidget()
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # 1. Barra Superior: Selector de Plataformas y Buscador
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        logo_label = QLabel("RETRO<b>SHELF</b>")
        logo_label.setStyleSheet("color: #7b6be8; font-size: 13pt; letter-spacing: 2px;")
        top_bar.addWidget(logo_label)

        # Contenedor desplazable de plataformas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(48)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.platforms_container = QWidget()
        self.platforms_layout = QHBoxLayout(self.platforms_container)
        self.platforms_layout.setContentsMargins(0, 0, 0, 0)
        self.platforms_layout.setSpacing(8)
        self.platforms_layout.addStretch()

        scroll.setWidget(self.platforms_container)
        top_bar.addWidget(scroll, 1)

        # Buscador rápido
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar… (Ctrl+F)")
        self.search_box.setFixedWidth(200)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(180)
        self.search_timer.timeout.connect(self._filter_games)
        self.search_box.textChanged.connect(lambda: self.search_timer.start())
        top_bar.addWidget(self.search_box)

        # Botón Pantalla Completa
        self.fullscreen_btn = QPushButton("⛶ Pantalla completa")
        self.fullscreen_btn.setProperty("class", "action-icon")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        top_bar.addWidget(self.fullscreen_btn)

        # Botón para abrir el Configurador si lo necesita
        config_btn = QPushButton("⚙ Configuración")
        config_btn.setProperty("class", "action-icon")
        config_btn.clicked.connect(self.open_configurator)
        top_bar.addWidget(config_btn)

        main_layout.addLayout(top_bar)

        # 2. Contenedor de Layouts Dinámicos (Grid, Showcase, Banners, Detalles)
        self.layout_stack = QStackedWidget()
        self.active_layouts = {}

        for l_name, l_cls in LAYOUT_REGISTRY.items():
            inst = l_cls()
            inst.game_selected.connect(self._on_game_selected)
            inst.game_activated.connect(self._on_game_activated)
            self.active_layouts[l_name] = inst
            self.layout_stack.addWidget(inst)

        main_layout.addWidget(self.layout_stack, 1)

        # 3. Barra inferior informativa y discreta
        self.bottom_bar = QFrame()
        self.bottom_bar.setStyleSheet("background-color: #161922; border-radius: 6px; padding: 6px 12px;")
        b_layout = QHBoxLayout(self.bottom_bar)
        b_layout.setContentsMargins(4, 4, 4, 4)

        self.status_label = QLabel("Seleccioná un elemento para comenzar")
        self.status_label.setStyleSheet("color: #8f9db3; font-size: 9pt;")
        b_layout.addWidget(self.status_label)
        b_layout.addStretch()

        tip_label = QLabel("F11: Pantalla completa  |  Enter: Seleccionar / Jugar  |  Esc / Retroceso: Volver")
        tip_label.setStyleSheet("color: #647087; font-size: 9pt;")
        b_layout.addWidget(tip_label)

        main_layout.addWidget(self.bottom_bar)

        self.setCentralWidget(root)

    def _setup_shortcuts(self):
        # F11 para pantalla completa
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)
        # Ctrl+F para buscar
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_box.setFocus)
        # Escape para retroceder o salir de pantalla completa
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._on_escape)
        # Backspace para retroceder en la navegación de menús
        QShortcut(QKeySequence(Qt.Key_Backspace), self, self._on_backspace)

    def _on_backspace(self):
        if self.search_box.hasFocus():
            return
        if self.navigation_history:
            prev_id = self.navigation_history.pop()
            self.select_list(prev_id, push_history=False)

    def _on_escape(self):
        if self.navigation_history:
            prev_id = self.navigation_history.pop()
            self.select_list(prev_id, push_history=False)
            return
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ Pantalla completa")
        elif self.search_box.hasFocus():
            self.search_box.clear()
            self.search_box.clearFocus()

    def apply_video_settings(self):
        """Pre-calcula la configuración de video para aplicarla una vez que la ventana sea visible."""
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()

        try:
            mon_idx = int(self.db.get_setting("video_monitor", "0"))
        except (ValueError, TypeError):
            mon_idx = 0

        target_screen = screens[mon_idx] if (screens and 0 <= mon_idx < len(screens)) else primary
        geo = target_screen.geometry() if target_screen else None

        mode = self.db.get_setting("video_mode", "windowed")  # windowed por defecto para evitar crashes
        res_key = self.db.get_setting("video_resolution", "native")

        if res_key == "custom":
            try:
                w = int(self.db.get_setting("video_custom_width", "1920"))
                h = int(self.db.get_setting("video_custom_height", "1080"))
            except (ValueError, TypeError):
                w, h = 1920, 1080
        elif res_key == "native" or "x" not in str(res_key):
            if geo:
                w = int(geo.width() * 0.9)
                h = int(geo.height() * 0.9)
            else:
                w, h = 1280, 800
        else:
            try:
                parts = str(res_key).split("x")
                w, h = int(parts[0]), int(parts[1])
            except Exception:
                w, h = 1280, 720

        # Guardar parámetros para aplicarlos en el showEvent
        self._pending_mode = mode
        self._pending_geo = geo
        self._pending_w = w
        self._pending_h = h
        self.configured_window_size = QSize(w, h)

    def _apply_show(self):
        """Aplica la configuración de ventana DESPUÉS de que el event loop está activo.
        Se llama via QTimer.singleShot desde run_player para evitar crashes en Windows."""
        from PySide6.QtCore import QTimer

        mode = getattr(self, "_pending_mode", "windowed")
        geo = getattr(self, "_pending_geo", None)
        w = getattr(self, "_pending_w", 1280)
        h = getattr(self, "_pending_h", 800)

        # Paso 1: Siempre abrir primero como ventana normal (evita crash de showFullScreen en Windows)
        self.showNormal()
        self.resize(w, h)
        if geo:
            cx = geo.x() + (geo.width() - w) // 2
            cy = geo.y() + (geo.height() - h) // 2
            try:
                self.move(max(geo.x(), cx), max(geo.y(), cy))
            except Exception:
                pass

        self.raise_()
        self.activateWindow()

        # Paso 2: Si el usuario eligió fullscreen, aplicarlo después de que Qt esté estabilizado
        if mode in ("fullscreen", "borderless"):
            def _go_fullscreen():
                try:
                    if geo:
                        self.move(geo.topLeft())
                    self.showFullScreen()
                    self.fullscreen_btn.setText("🗗 Ventana")
                except Exception:
                    pass  # Si falla el fullscreen, quedamos en ventana normal
            QTimer.singleShot(200, _go_fullscreen)
        else:
            self.fullscreen_btn.setText("⛶ Pantalla completa")



    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            if hasattr(self, "configured_window_size") and self.configured_window_size.isValid():
                self.resize(self.configured_window_size)
            self.fullscreen_btn.setText("⛶ Pantalla completa")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("🗗 Ventana")

    def open_configurator(self):
        """Abre el configurador sin cerrar el reproductor."""
        from retroshelf.ui.main_window import MainWindow
        self.config_window = MainWindow()
        self.config_window.show()

    def load_lists(self):
        """Carga las listas/consolas configuradas en la barra superior."""
        # Limpiar botones anteriores
        for btn in self.platform_buttons:
            self.platforms_layout.removeWidget(btn)
            btn.deleteLater()
        self.platform_buttons.clear()

        rows = self.db.all(
            """SELECT l.*, COUNT(g.id) AS game_count
               FROM game_lists l
               LEFT JOIN games g ON g.list_id = l.id
               GROUP BY l.id
               ORDER BY l.name COLLATE NOCASE"""
        )

        if not rows:
            self.status_label.setText("No hay listas creadas. Abrí el Configurador para crear listas y añadir juegos.")
            return

        for idx, row in enumerate(rows):
            name = row["name"]
            is_menu = (row["list_type"] == "menu") if "list_type" in row.keys() else False
            if is_menu:
                sub_items = self.db.get_menu_items(row["id"])
                btn = QPushButton(f"🧭 {name} ({len(sub_items)})")
            else:
                count = row["game_count"]
                btn = QPushButton(f"{name} ({count})")
            btn.setProperty("class", "platform-btn")
            btn.setCheckable(True)
            list_id = row["id"]
            btn.clicked.connect(lambda checked=False, lid=list_id: self.select_list(lid, push_history=True))
            self.platforms_layout.insertWidget(idx, btn)
            self.platform_buttons.append((list_id, btn))

        # Seleccionar la primera lista por defecto
        if self.platform_buttons:
            self.select_list(self.platform_buttons[0][0], push_history=False)

    def _get_or_create_layout(self, layout_name: str):
        """Obtiene una instancia del layout o la crea dinámicamente si es un tema de sistema."""
        if layout_name in self.active_layouts:
            return self.active_layouts[layout_name]

        # Crear dinámicamente
        inst = create_layout(layout_name)
        inst.db = self.db
        inst.game_selected.connect(self._on_game_selected)
        inst.game_activated.connect(self._on_game_activated)
        self.active_layouts[layout_name] = inst
        self.layout_stack.addWidget(inst)
        return inst

    def select_list(self, list_id: int, push_history: bool = True):
        if push_history and self.current_list_id and self.current_list_id != list_id:
            self.navigation_history.append(self.current_list_id)

        self.current_list_id = list_id

        # Actualizar estado 'checked' de los botones
        for lid, btn in self.platform_buttons:
            btn.setChecked(lid == list_id)

        row = self.db.one("SELECT * FROM game_lists WHERE id=?", (list_id,))
        if not row:
            return

        # Aplicar el layout asignado a esta lista o buscar si coincide con un tema
        chosen_layout = row["layout"] or ""
        platform_name = row["platform"] or ""
        list_name = row["name"] or ""

        available = get_available_layouts()

        # Determinar el layout objetivo
        if chosen_layout in available:
            target_layout = chosen_layout
        elif resolve_theme_name(chosen_layout):
            target_layout = resolve_theme_name(chosen_layout)
        elif platform_name in available:
            target_layout = platform_name
        elif resolve_theme_name(platform_name):
            target_layout = resolve_theme_name(platform_name)
        elif list_name in available:
            target_layout = list_name
        elif resolve_theme_name(list_name):
            target_layout = resolve_theme_name(list_name)
        else:
            target_layout = "Grid"

        inst = self._get_or_create_layout(target_layout)
        # Detener multimedia del layout anterior para evitar audio residual
        previous = self.layout_stack.currentWidget()
        if previous and previous is not inst and hasattr(previous, 'stop_media'):
            previous.stop_media()
        self.layout_stack.setCurrentWidget(inst)
        inst.setFocus()

        self.current_game_id = None
        self.load_games()

    def load_games(self):
        if not self.current_list_id:
            self.games_cache = []
            return

        row = self.db.one("SELECT * FROM game_lists WHERE id=?", (self.current_list_id,))
        if not row:
            return

        term = self.search_box.text().strip().lower()

        if "list_type" in row.keys() and row["list_type"] == "menu":
            menu_media_path = row["media_path"] if "media_path" in row.keys() else ""
            menu_boxart_path = row["boxart_path"] if "boxart_path" in row.keys() else ""
            menu_wheel_path = row["wheel_path"] if "wheel_path" in row.keys() else ""
            menu_video_path = row["video_path"] if "video_path" in row.keys() else ""
            menu_cartart_path = row["cartart_path"] if "cartart_path" in row.keys() else ""

            targets = self.db.get_menu_items(self.current_list_id)
            items = []
            for t in targets:
                t_dict = dict(t)
                title = t_dict["name"]
                platform = t_dict["platform"] or title
                if term and (term not in title.lower() and term not in platform.lower()):
                    continue
                cnt_row = self.db.one("SELECT COUNT(*) as c FROM games WHERE list_id=?", (t_dict["id"],))
                g_count = cnt_row["c"] if cnt_row else 0
                items.append({
                    "id": t_dict["id"],
                    "target_list_id": t_dict["id"],
                    "is_menu_target": True,
                    "title": title,
                    "rom_path": "",
                    "list_id": self.current_list_id,
                    "platform": platform,
                    "media_path": menu_media_path or t_dict.get("media_path") or "",
                    "boxart_path": menu_boxart_path or t_dict.get("boxart_path") or "",
                    "wheel_path": menu_wheel_path or t_dict.get("wheel_path") or "",
                    "video_path": menu_video_path or t_dict.get("video_path") or "",
                    "cartart_path": menu_cartart_path or t_dict.get("cartart_path") or "",
                    "menu_media_path": menu_media_path,
                    "menu_wheel_path": menu_wheel_path,
                    "menu_video_path": menu_video_path,
                    "menu_boxart_path": menu_boxart_path,
                    "menu_cartart_path": menu_cartart_path,
                    "effective_name": f"{g_count} juegos",
                    "source": "menu",
                })
            self.games_cache = items
            current_layout = self.layout_stack.currentWidget()
            if current_layout:
                current_layout.set_games(self.games_cache)
                if self.games_cache:
                    first_id = self.games_cache[0]["id"]
                    current_layout.select_game_by_id(first_id)
                    self._on_game_selected(first_id)
                else:
                    self.status_label.setText("No hay sistemas en este menú. Agregalos desde el Configurador.")
            return

        rows = self.db.all(
            """SELECT g.*, l.default_emulator_id, l.platform,
               l.boxart_path, l.wheel_path, l.video_path, l.cartart_path, l.media_path,
               COALESCE(override.name, base.name, 'Sin emulador') AS effective_name,
               CASE
                   WHEN g.emulator_override_id IS NOT NULL THEN 'juego'
                   WHEN l.default_emulator_id IS NOT NULL THEN 'lista'
                   ELSE 'ninguno'
               END AS source
               FROM games g
               JOIN game_lists l ON l.id = g.list_id
               LEFT JOIN emulators override ON override.id = g.emulator_override_id
               LEFT JOIN emulators base ON base.id = l.default_emulator_id
               WHERE g.list_id = ? AND (g.title LIKE ? OR g.rom_path LIKE ?)
               ORDER BY g.title COLLATE NOCASE""",
            (self.current_list_id, f"%{term}%", f"%{term}%")
        )
        self.games_cache = [dict(r) for r in rows]

        current_layout = self.layout_stack.currentWidget()

        if current_layout:
            current_layout.set_games(self.games_cache)
            if self.games_cache:
                first_id = self.games_cache[0]["id"]
                current_layout.select_game_by_id(first_id)
                self._on_game_selected(first_id)
            else:
                self.status_label.setText("No hay juegos en esta lista. Añadí juegos en el Configurador.")

    def _filter_games(self):
        self.load_games()

    def _on_game_selected(self, game_id: int):
        self.current_game_id = game_id
        game = next((g for g in self.games_cache if g["id"] == game_id), None)
        if game:
            if game.get("is_menu_target"):
                self.status_label.setText(
                    f"🧭 <b>{game['title']}</b>   |   {game.get('effective_name', '')}   |   Enter: Entrar al sistema  |  Esc / Retroceso: Volver"
                )
            else:
                emu = game.get("effective_name", "Sin emulador")
                self.status_label.setText(f"🎮 <b>{game['title']}</b>   |   Emulador: {emu}")

    def _on_game_activated(self, game_id: int):
        self.current_game_id = game_id
        game = next((g for g in self.games_cache if g["id"] == game_id), None)
        if game and game.get("is_menu_target"):
            target_id = game["target_list_id"]
            self.select_list(target_id, push_history=True)
            return

        db_game = self.db.one("SELECT * FROM games WHERE id=?", (game_id,))
        if not db_game:
            return

        try:
            self.status_label.setText(f"Iniciando <b>{db_game['title']}</b>...")
            QApplication.processEvents()
            active_layout = self.layout_stack.currentWidget()
            emu_name, source = launch_game(self.db, db_game, layout=active_layout, parent_window=self)
            self.status_label.setText(f"Ejecutando <b>{db_game['title']}</b> con {emu_name}")
        except Exception as e:
            QMessageBox.critical(self, "No se pudo iniciar el juego", str(e))
            self.status_label.setText("Error al ejecutar el juego.")

    def closeEvent(self, event):
        """Detiene cualquier reproducción activa antes de cerrar la ventana."""
        for inst in self.active_layouts.values():
            if hasattr(inst, "player") and inst.player:
                try:
                    inst.player.stop()
                except Exception:
                    pass
        super().closeEvent(event)


def run_player():
    import os
    from PySide6.QtCore import QTimer
    try:
        from retroshelf.db import Database
        db = Database()
        driver = db.get_setting("video_driver", "d3d11")
        if driver:
            os.environ["QSG_RHI_BACKEND"] = driver
            os.environ["QT_RHI_BACKEND"] = driver
    except Exception:
        pass

    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("RetroShelf Player")
    window = PlayerWindow()
    # Pre-calcular la configuración (sin abrir ventana todavía)
    window.apply_video_settings()
    # Mostrar la ventana dentro del event loop para evitar crashes de acceso a memoria en Windows
    QTimer.singleShot(0, window._apply_show)
    code = app.exec()
    os._exit(code)


