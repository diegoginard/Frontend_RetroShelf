"""
Pestaña de Configuración del Sistema para RetroShelf.
Permite configurar:
1. Asignación interactiva de controles y teclas (Cerrar emulador, subir/bajar ruleta, seleccionar, silenciar, etc.).
2. Comportamiento del emulador (silenciar videos al ejecutar, tecla de cierre global, combo de gamepad).
3. Configuración de pantalla y video del Frontend (modo de pantalla, resolución, monitor y escala).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QCheckBox, QComboBox,
    QSpinBox, QDialog, QMessageBox, QFrame, QScrollArea, QAbstractItemView
)
from retroshelf.services.controls import (
    ACTIONS_INFO, get_all_bindings, set_binding, reset_default_bindings,
    qt_key_to_name
)

SCREEN_MODES = [
    ("Pantalla completa exclusiva (Fullscreen)", "fullscreen"),
    ("Ventana sin bordes (Borderless Window)", "borderless"),
    ("Modo ventana estándar", "windowed")
]

RESOLUTIONS_LIST = [
    ("Nativa del monitor (Recomendado)", "native"),
    ("1920 x 1080 (Full HD 1080p)", "1920x1080"),
    ("2560 x 1440 (2K QHD)", "2560x1440"),
    ("3840 x 2160 (4K UHD)", "3840x2160"),
    ("1280 x 720 (HD 720p)", "1280x720"),
    ("1024 x 768 (4:3 CRT Retro)", "1024x768"),
    ("1600 x 900", "1600x900"),
    ("Personalizada...", "custom")
]

GRAPHICS_ENGINES = [
    ("DirectX 11 (Direct3D 11 - Recomendado en Windows)", "d3d11"),
    ("DirectX 12 (Direct3D 12)", "d3d12"),
    ("OpenGL (Estándar multiplataforma)", "opengl"),
    ("Vulkan (Alto rendimiento)", "vulkan"),
]


class KeyCaptureDialog(QDialog):
    """
    Diálogo modal interactivo para capturar una tecla presionada por el usuario.
    """
    def __init__(self, action_name: str, parent=None):
        super().__init__(parent)
        self.action_name = action_name
        self.captured_key_name: str | None = None

        self.setWindowTitle("Asignar tecla")
        self.setFixedSize(420, 220)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1d27;
                border: 2px solid #5d48d9;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl_title = QLabel(f"Asignando control para:")
        lbl_title.setStyleSheet("color: #9aa5b8; font-size: 10pt;")
        layout.addWidget(lbl_title)

        lbl_action = QLabel(f"<b>{action_name}</b>")
        lbl_action.setStyleSheet("color: #ffffff; font-size: 13pt;")
        layout.addWidget(lbl_action)

        self.key_box = QFrame()
        self.key_box.setStyleSheet("""
            QFrame {
                background-color: #242938;
                border: 2px dashed #7866ed;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        kb_layout = QVBoxLayout(self.key_box)
        self.status_label = QLabel("Presioná una tecla en el teclado...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e2e8f0; font-size: 11pt; font-weight: bold;")
        kb_layout.addWidget(self.status_label)
        layout.addWidget(self.key_box)

        hint = QLabel("Presioná la tecla que querés asignar (ej: Escape, Espacio, W, Enter...)")
        hint.setStyleSheet("color: #718096; font-size: 9pt;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        # Ignorar teclas modificadoras solas
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            event.accept()
            return

        name = qt_key_to_name(key)
        self.captured_key_name = name
        self.accept()


class SystemSettingsWidget(QWidget):
    """
    Panel integrado de Configuración del Sistema para RetroShelf.
    """
    settings_saved = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Encabezado principal
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #1b1e2a; border-radius: 8px; padding: 12px;")
        h_layout = QVBoxLayout(header_card)
        title = QLabel("⚙ Configuración del Sistema y Controles")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        h_layout.addWidget(title)

        desc = QLabel(
            "Configurá los controles del teclado para navegar por las ruletas y listas, "
            "el comportamiento al ejecutar emuladores (mute y tecla de cierre global), y las opciones de video."
        )
        desc.setStyleSheet("color: #9aa5b8; font-size: 10pt;")
        desc.setWordWrap(True)
        h_layout.addWidget(desc)
        layout.addWidget(header_card)

        # -------------------------------------------------------------
        # 1. Grupo: Controles y Asignación de Teclas
        # -------------------------------------------------------------
        grp_controls = QGroupBox("🎮 Controles y Asignación de Teclas del Sistema")
        v_controls = QVBoxLayout(grp_controls)
        v_controls.setSpacing(10)

        lbl_c_info = QLabel(
            "Hacé clic en <b>'Cambiar Tecla'</b> en cualquier acción para asignar la tecla deseada. "
            "Estas teclas controlan la ruleta, la selección de juegos y el cierre global de emuladores."
        )
        lbl_c_info.setStyleSheet("color: #a0aec0; font-size: 9pt;")
        lbl_c_info.setWordWrap(True)
        v_controls.addWidget(lbl_c_info)

        self.controls_table = QTableWidget()
        self.controls_table.setColumnCount(4)
        self.controls_table.setHorizontalHeaderLabels(["Acción", "Descripción", "Tecla Actual", "Asignar"])
        self.controls_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.controls_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.controls_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.controls_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.controls_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.controls_table.verticalHeader().setVisible(False)
        self.controls_table.setMinimumHeight(240)
        v_controls.addWidget(self.controls_table)

        row_c_btns = QHBoxLayout()
        btn_reset_keys = QPushButton("↺ Restablecer controles predeterminados")
        btn_reset_keys.clicked.connect(self._reset_controls_defaults)
        row_c_btns.addWidget(btn_reset_keys)
        row_c_btns.addStretch(1)
        v_controls.addLayout(row_c_btns)

        layout.addWidget(grp_controls)

        # -------------------------------------------------------------
        # 2. Grupo: Comportamiento de Emuladores
        # -------------------------------------------------------------
        grp_emu = QGroupBox("🕹 Comportamiento de Emuladores")
        v_emu = QVBoxLayout(grp_emu)
        v_emu.setSpacing(10)

        self.chk_mute_video = QCheckBox("Silenciar audio de los videos snaps automáticamente al ejecutar un emulador")
        self.chk_mute_video.setStyleSheet("font-weight: 500; font-size: 10pt;")
        v_emu.addWidget(self.chk_mute_video)

        lbl_mute_hint = QLabel("Al salir del emulador, el sonido del video snap en el diseño visual se reanuda de inmediato.")
        lbl_mute_hint.setStyleSheet("color: #718096; font-size: 9pt; margin-left: 24px;")
        v_emu.addWidget(lbl_mute_hint)

        self.chk_global_exit = QCheckBox("Permitir cerrar el emulador en ejecución con la tecla asignada (ej: Escape)")
        self.chk_global_exit.setStyleSheet("font-weight: 500; font-size: 10pt;")
        v_emu.addWidget(self.chk_global_exit)

        lbl_exit_hint = QLabel("Monitorea globalmente en Windows la tecla configurada y cierra el emulador de forma limpia al presionarla.")
        lbl_exit_hint.setStyleSheet("color: #718096; font-size: 9pt; margin-left: 24px;")
        v_emu.addWidget(lbl_exit_hint)

        self.chk_gamepad_exit = QCheckBox("Permitir cerrar el emulador con combo de control / gamepad (Back + Start)")
        self.chk_gamepad_exit.setStyleSheet("font-weight: 500; font-size: 10pt;")
        v_emu.addWidget(self.chk_gamepad_exit)

        layout.addWidget(grp_emu)

        # -------------------------------------------------------------
        # 3. Grupo: Pantalla y Video (Frontend)
        # -------------------------------------------------------------
        grp_video = QGroupBox("🖥 Pantalla y Video del Frontend")
        v_video = QVBoxLayout(grp_video)
        v_video.setSpacing(12)

        row_v1 = QHBoxLayout()
        row_v1.setSpacing(16)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Modo de pantalla:"))
        self.mode_combo = QComboBox()
        for label, val in SCREEN_MODES:
            self.mode_combo.addItem(label, val)
        col1.addWidget(self.mode_combo)
        row_v1.addLayout(col1, 1)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Resolución:"))
        self.res_combo = QComboBox()
        for label, val in RESOLUTIONS_LIST:
            self.res_combo.addItem(label, val)
        col2.addWidget(self.res_combo)
        row_v1.addLayout(col2, 1)

        v_video.addLayout(row_v1)

        row_v2 = QHBoxLayout()
        row_v2.setSpacing(16)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Motor gráfico / API de video:"))
        self.driver_combo = QComboBox()
        for label, val in GRAPHICS_ENGINES:
            self.driver_combo.addItem(label, val)
        col3.addWidget(self.driver_combo)
        row_v2.addLayout(col3, 1)

        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Monitor de destino:"))
        self.screen_combo = QComboBox()
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()
        for idx, scr in enumerate(screens):
            geo = scr.geometry()
            tag = " [Principal]" if scr == primary else ""
            self.screen_combo.addItem(f"Monitor {idx + 1}: {geo.width()}x{geo.height()}{tag}", idx)
        col4.addWidget(self.screen_combo)
        row_v2.addLayout(col4, 1)

        v_video.addLayout(row_v2)

        lbl_driver_hint = QLabel("💡 <i>Nota: El cambio de motor gráfico (DirectX 11, DirectX 12, OpenGL o Vulkan) se aplicará la próxima vez que inicies RetroShelf.</i>")
        lbl_driver_hint.setStyleSheet("color: #9aa5b8; font-size: 8.5pt;")
        v_video.addWidget(lbl_driver_hint)

        layout.addWidget(grp_video)

        # Barra inferior de guardado
        save_bar = QHBoxLayout()
        save_bar.addStretch(1)

        self.save_btn = QPushButton("💾 Guardar Configuración del Sistema")
        self.save_btn.setObjectName("primary")
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setMinimumWidth(260)
        self.save_btn.clicked.connect(self.save_all)
        save_bar.addWidget(self.save_btn)

        layout.addLayout(save_bar)
        layout.addStretch(1)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

        self.refresh_controls_table()
        self.load_settings()

    def refresh_controls_table(self):
        """Llena la tabla de asignación de teclas."""
        bindings = get_all_bindings(self.db)
        self.controls_table.setRowCount(len(bindings))

        for row, info in enumerate(bindings):
            item_name = QTableWidgetItem(info["name"])
            item_name.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.controls_table.setItem(row, 0, item_name)

            item_desc = QTableWidgetItem(info["desc"])
            item_desc.setForeground(Qt.gray)
            self.controls_table.setItem(row, 1, item_desc)

            key_badge = QTableWidgetItem(f"  {info['key']}  ")
            key_badge.setTextAlignment(Qt.AlignCenter)
            key_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.controls_table.setItem(row, 2, key_badge)

            btn_change = QPushButton("Cambiar Tecla…")
            btn_change.setProperty("action_id", info["id"])
            btn_change.setProperty("action_name", info["name"])
            btn_change.clicked.connect(lambda checked=False, i=info: self._prompt_key_change(i["id"], i["name"]))
            self.controls_table.setCellWidget(row, 3, btn_change)

    def _prompt_key_change(self, action_id: str, action_name: str):
        dialog = KeyCaptureDialog(action_name, self)
        if dialog.exec() and dialog.captured_key_name:
            new_key = dialog.captured_key_name
            set_binding(self.db, action_id, new_key)
            self.refresh_controls_table()
            self.settings_saved.emit()

    def _reset_controls_defaults(self):
        res = QMessageBox.question(
            self,
            "Restablecer controles",
            "¿Deseás restablecer todas las teclas y controles a sus valores predeterminados?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            reset_default_bindings(self.db)
            self.refresh_controls_table()
            self.settings_saved.emit()

    def load_settings(self):
        """Carga las opciones de emuladores y pantalla desde la base de datos."""
        if not self.db:
            return

        # Emulador
        self.chk_mute_video.setChecked(self.db.get_setting("emulator_mute_video", "true").lower() == "true")
        self.chk_global_exit.setChecked(self.db.get_setting("emulator_global_exit", "true").lower() == "true")
        self.chk_gamepad_exit.setChecked(self.db.get_setting("emulator_gamepad_exit", "true").lower() == "true")

        # Video
        mode = self.db.get_setting("video_mode", "fullscreen")
        idx_mode = self.mode_combo.findData(mode)
        if idx_mode != -1:
            self.mode_combo.setCurrentIndex(idx_mode)

        res = self.db.get_setting("video_resolution", "native")
        idx_res = self.res_combo.findData(res)
        if idx_res != -1:
            self.res_combo.setCurrentIndex(idx_res)

        driver = self.db.get_setting("video_driver", "d3d11")
        idx_driver = self.driver_combo.findData(driver)
        if idx_driver != -1:
            self.driver_combo.setCurrentIndex(idx_driver)

        target_screen = int(self.db.get_setting("target_screen", "0") or "0")
        if 0 <= target_screen < self.screen_combo.count():
            self.screen_combo.setCurrentIndex(target_screen)

    def save_all(self):
        """Guarda todas las configuraciones en la base de datos."""
        if not self.db:
            return

        # Emulador
        self.db.set_setting("emulator_mute_video", "true" if self.chk_mute_video.isChecked() else "false")
        self.db.set_setting("emulator_global_exit", "true" if self.chk_global_exit.isChecked() else "false")
        self.db.set_setting("emulator_gamepad_exit", "true" if self.chk_gamepad_exit.isChecked() else "false")

        # Video
        mode = self.mode_combo.currentData()
        self.db.set_setting("video_mode", mode)

        res = self.res_combo.currentData()
        self.db.set_setting("video_resolution", res)

        driver = self.driver_combo.currentData()
        self.db.set_setting("video_driver", driver)

        target_screen = self.screen_combo.currentData()
        self.db.set_setting("target_screen", str(target_screen if target_screen is not None else 0))

        self.settings_saved.emit()
        QMessageBox.information(
            self,
            "Configuración guardada",
            "La configuración del sistema, controles y video fue guardada exitosamente.\n\n"
            "Si cambiaste el motor gráfico, este se aplicará la próxima vez que inicies RetroShelf."
        )
