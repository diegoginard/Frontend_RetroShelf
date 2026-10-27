from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton,
    QDialogButtonBox, QFileDialog, QMessageBox, QHBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QGroupBox,
    QTextEdit, QAbstractItemView, QCheckBox, QSpinBox, QFrame,
    QListWidget, QListWidgetItem, QScrollArea
)
from retroshelf.services.library import normalize_extensions, parse_extensions_list
from retroshelf.services.media import detect_media_folders
from retroshelf.services.themes import get_layout_media_spec

PRESET_EXTENSIONS = {
    "Personalizado...": ("", ""),
    "Super Nintendo (SNES)": ("Super Nintendo", ".sfc;.smc;.zip"),
    "Game Boy Advance (GBA)": ("Game Boy Advance", ".gba;.zip;.7z"),
    "PlayStation (PS1)": ("PlayStation", ".cue;.bin;.iso;.chd;.pbp"),
    "PlayStation 2 (PS2)": ("PlayStation 2", ".iso;.chd;.cso;.bin"),
    "Sega Genesis / Mega Drive": ("Mega Drive", ".md;.gen;.smd;.bin"),
    "Nintendo 64 (N64)": ("Nintendo 64", ".z64;.n64;.v64;.zip"),
    "Nintendo DS (NDS)": ("Nintendo DS", ".nds;.zip;.7z"),
    "PSP": ("PlayStation Portable", ".iso;.cso;.pbp"),
    "Arcade (MAME / FBNeo)": ("Arcade", ".zip;.7z;.chd")
}

class ListDialog(QDialog):
    """
    Diálogo para crear o editar una lista de juegos o un Menú de Sistemas (lista de listas).
    """
    def __init__(self, emulators, parent=None, existing=None, all_lists=None, initial_menu_items=None):
        super().__init__(parent)
        self.existing = existing
        self.all_lists = all_lists or []
        self.initial_menu_items = initial_menu_items or []
        self.setWindowTitle("Editar lista / menú" if existing else "Crear nueva lista / menú")
        self.setMinimumWidth(620)
        self.normalized_exts = ""

        # Layout principal del diálogo
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Contenedor desplazable con soporte de rueda de ratón
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 8, 0)
        scroll_layout.setSpacing(10)

        # 1. Cabecera básica: Nombre, Tipo de Lista, Plataforma
        basic_group = QGroupBox("Información Principal")
        form = QFormLayout(basic_group)
        form.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ej: Super Nintendo, Menú de Consolas...")
        form.addRow("Nombre *", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItem("🎮 Lista de juegos (ROMs y emulador)", "games")
        self.type_combo.addItem("🧭 Menú de sistemas (Lista de listas)", "menu")
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Tipo de lista", self.type_combo)

        self.platform_edit = QLineEdit()
        self.platform_edit.setPlaceholderText("Ej: Super Nintendo, GBA, Arcade...")
        form.addRow("Plataforma o etiqueta", self.platform_edit)

        from retroshelf.ui.layouts import get_available_layouts
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(get_available_layouts())
        form.addRow("Diseño visual", self.layout_combo)

        scroll_layout.addWidget(basic_group)

        # 2. Grupo para Lista de Juegos (ROMs, Emulador, Extensiones)
        self.game_settings_group = QGroupBox("Configuración de Juegos y Emulador")
        game_form = QFormLayout(self.game_settings_group)
        game_form.setSpacing(8)

        self.preset_combo = QComboBox()
        for title in PRESET_EXTENSIONS.keys():
            self.preset_combo.addItem(title)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        game_form.addRow("Plantilla sugerida", self.preset_combo)

        self.extensions_edit = QLineEdit()
        self.extensions_edit.setPlaceholderText("Ej: .sfc;.smc;.zip (separadas por ;)")
        game_form.addRow("Extensiones admitidas *", self.extensions_edit)

        ext_hint = QLabel(
            "<b>Obligatorio:</b> Escribí las extensiones permitidas separadas <b>exclusivamente por punto y coma (;)</b>.<br>"
            "<i>Ejemplo: .cue;.bin;.chd;.iso</i>"
        )
        ext_hint.setStyleSheet("color: #aab1c0; font-size: 9pt;")
        ext_hint.setWordWrap(True)
        game_form.addRow("", ext_hint)

        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Seleccionar carpeta donde están los juegos...")
        browse_folder_btn = QPushButton("Examinar…")
        browse_folder_btn.clicked.connect(self.pick_folder)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_edit, 1)
        folder_row.addWidget(browse_folder_btn)
        folder_holder = QWidget()
        folder_holder.setLayout(folder_row)
        game_form.addRow("Carpeta de juegos", folder_holder)

        self.auto_scan_checkbox = QCheckBox("Escanear e importar juegos de esta carpeta automáticamente")
        self.auto_scan_checkbox.setChecked(True if not existing else False)
        game_form.addRow("", self.auto_scan_checkbox)

        self.emulator_combo = QComboBox()
        self.emulator_combo.addItem("Sin emulador predeterminado", None)
        for e in emulators:
            self.emulator_combo.addItem(e["name"], e["id"])
        game_form.addRow("Emulador predeterminado", self.emulator_combo)

        scroll_layout.addWidget(self.game_settings_group)

        # 3. Grupo para Menú de Sistemas (Selección y orden de listas vinculadas)
        self.menu_settings_group = QGroupBox("Sistemas a incluir en este Menú")
        menu_layout = QVBoxLayout(self.menu_settings_group)
        menu_layout.setSpacing(8)

        menu_hint = QLabel("Marcá las listas que formarán parte de este menú y utilizá las flechas para definir el orden:")
        menu_hint.setStyleSheet("color: #aab1c0; font-size: 9pt;")
        menu_hint.setWordWrap(True)
        menu_layout.addWidget(menu_hint)

        list_and_controls = QHBoxLayout()
        self.sublists_list = QListWidget()
        self.sublists_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sublists_list.setStyleSheet(
            "QListWidget { background-color: #171a23; border: 1px solid #2a3143; border-radius: 6px; padding: 4px; }"
            "QListWidget::item { padding: 4px; border-radius: 4px; }"
            "QListWidget::item:hover { background-color: #23293a; }"
            "QListWidget::item:selected { background-color: #5d48d9; color: white; }"
        )
        list_and_controls.addWidget(self.sublists_list, 1)

        # Botones de orden y selección
        btn_vbox = QVBoxLayout()
        btn_vbox.setSpacing(6)

        up_btn = QPushButton("▲ Subir")
        up_btn.clicked.connect(self._move_item_up)
        btn_vbox.addWidget(up_btn)

        down_btn = QPushButton("▼ Bajar")
        down_btn.clicked.connect(self._move_item_down)
        btn_vbox.addWidget(down_btn)

        btn_vbox.addSpacing(10)

        check_all_btn = QPushButton("Marcar todas")
        check_all_btn.clicked.connect(lambda: self._check_all_lists(True))
        btn_vbox.addWidget(check_all_btn)

        uncheck_all_btn = QPushButton("Desmarcar")
        uncheck_all_btn.clicked.connect(lambda: self._check_all_lists(False))
        btn_vbox.addWidget(uncheck_all_btn)

        btn_vbox.addStretch()
        list_and_controls.addLayout(btn_vbox)
        menu_layout.addLayout(list_and_controls)

        scroll_layout.addWidget(self.menu_settings_group)

        # 4. Sección de Medios y Arte (especificada dinámicamente según el diseño visual)
        media_group = QGroupBox("Carpetas de Medios y Arte (Opcional)")
        self.media_group = media_group
        media_layout = QFormLayout(media_group)
        media_layout.setSpacing(8)

        # Carpeta raíz de Medios
        self.media_root_edit = QLineEdit()
        self.media_root_edit.setPlaceholderText("Carpeta principal 'media' (ej: C:/Juegos/SNES/media)...")
        browse_media_root_btn = QPushButton("Examinar…")
        browse_media_root_btn.clicked.connect(self.pick_media_root)

        media_root_row = QHBoxLayout()
        media_root_row.setContentsMargins(0, 0, 0, 0)
        media_root_row.addWidget(self.media_root_edit, 1)
        media_root_row.addWidget(browse_media_root_btn)
        media_root_widget = QWidget()
        media_root_widget.setLayout(media_root_row)
        media_layout.addRow("Carpeta Media (Raíz):", media_root_widget)

        self.auto_det_row_widget = QWidget()
        auto_det_row = QHBoxLayout(self.auto_det_row_widget)
        auto_det_row.setContentsMargins(0, 0, 0, 0)
        auto_det_btn = QPushButton("🔍 Auto-detectar subcarpetas según el diseño visual")
        auto_det_btn.clicked.connect(lambda: self.auto_detect_media(silent=False))
        auto_det_row.addWidget(auto_det_btn)
        auto_det_row.addStretch()
        media_layout.addRow("", self.auto_det_row_widget)

        # Contenedor wrapper para alojar el formulario dinámico de medios
        self.dynamic_media_wrapper = QWidget()
        self.dynamic_media_wrapper_layout = QVBoxLayout(self.dynamic_media_wrapper)
        self.dynamic_media_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_media_wrapper_layout.setSpacing(0)
        media_layout.addRow(self.dynamic_media_wrapper)

        self.dynamic_media_container = None
        self.media_edits = {}
        self._media_values = {}

        scroll_layout.addWidget(media_group)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # 5. Botones de acción siempre fijos y visibles en la parte inferior
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Adaptar dinámicamente el tamaño inicial a la pantalla disponible
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail_geo = screen.availableGeometry()
            target_h = min(680, int(avail_geo.height() * 0.85))
            self.resize(620, target_h)
        else:
            self.resize(620, 650)

        # Poblar listas vinculadas
        self._populate_sublists()

        # Cargar valores si es edición
        if existing:
            self.name_edit.setText(existing["name"])
            self.platform_edit.setText(existing["platform"] or "")
            self.extensions_edit.setText(existing["allowed_extensions"] or "")
            self.folder_edit.setText(existing["roms_path"] or "" if "roms_path" in existing.keys() else "")
            idx = self.emulator_combo.findData(existing["default_emulator_id"])
            if idx >= 0:
                self.emulator_combo.setCurrentIndex(idx)
            self.layout_combo.setCurrentText(existing["layout"] or "Wheel")

            list_type = existing["list_type"] if "list_type" in existing.keys() else "games"
            idx_t = self.type_combo.findData(list_type)
            if idx_t >= 0:
                self.type_combo.setCurrentIndex(idx_t)

            if "media_path" in existing.keys() and existing["media_path"]:
                self.media_root_edit.setText(existing["media_path"])
            if "boxart_path" in existing.keys() and existing["boxart_path"]:
                self._media_values["boxart"] = existing["boxart_path"]
            if "wheel_path" in existing.keys() and existing["wheel_path"]:
                self._media_values["wheel"] = existing["wheel_path"]
            if "video_path" in existing.keys() and existing["video_path"]:
                self._media_values["video"] = existing["video_path"]
            if "cartart_path" in existing.keys() and existing["cartart_path"]:
                self._media_values["cartart"] = existing["cartart_path"]
        else:
            self.type_combo.setCurrentIndex(0)

        # Conectar cambio de layout para reconstruir dinámicamente las carpetas de medios esperadas
        self.layout_combo.currentTextChanged.connect(self._rebuild_dynamic_media_ui)
        self._rebuild_dynamic_media_ui()

        self._on_type_changed()

    def _populate_sublists(self):
        self.sublists_list.clear()
        excluded_id = self.existing["id"] if self.existing else None

        initial_ids = [m["id"] for m in self.initial_menu_items]
        # Mapa de todas las listas disponibles
        lists_map = {l["id"]: dict(l) for l in self.all_lists if l["id"] != excluded_id}

        # 1. Agregar primero las ya vinculadas en su orden guardado
        for m_id in initial_ids:
            if m_id in lists_map:
                l_info = lists_map.pop(m_id)
                self._add_sublist_item(l_info, checked=True)

        # 2. Agregar las restantes
        for l_info in lists_map.values():
            checked = (self.existing is None)
            self._add_sublist_item(l_info, checked=checked)

    def _add_sublist_item(self, list_info: dict, checked: bool):
        plat = list_info.get("platform") or "Sin definir"
        is_menu = (list_info.get("list_type") == "menu")
        prefix = "🧭 " if is_menu else "🎮 "
        item = QListWidgetItem(f"{prefix}{list_info['name']}   [{plat}]")
        item.setData(Qt.UserRole, list_info["id"])
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.sublists_list.addItem(item)

    def _move_item_up(self):
        row = self.sublists_list.currentRow()
        if row > 0:
            item = self.sublists_list.takeItem(row)
            self.sublists_list.insertItem(row - 1, item)
            self.sublists_list.setCurrentRow(row - 1)

    def _move_item_down(self):
        row = self.sublists_list.currentRow()
        if row >= 0 and row < self.sublists_list.count() - 1:
            item = self.sublists_list.takeItem(row)
            self.sublists_list.insertItem(row + 1, item)
            self.sublists_list.setCurrentRow(row + 1)

    def _check_all_lists(self, checked: bool):
        state = Qt.Checked if checked else Qt.Unchecked
        for i in range(self.sublists_list.count()):
            self.sublists_list.item(i).setCheckState(state)

    def _on_type_changed(self):
        is_menu = (self.type_combo.currentData() == "menu")
        self.game_settings_group.setVisible(not is_menu)
        self.menu_settings_group.setVisible(is_menu)
        self.auto_det_row_widget.setVisible(True)
        if is_menu:
            if not self.platform_edit.text().strip():
                self.platform_edit.setText("Menú Principal")
            if not self.name_edit.text().strip():
                self.name_edit.setText("Sistemas")

    def _rebuild_dynamic_media_ui(self):
        """
        Reconstruye dinámicamente las filas de medios según lo especificado en el layout.json
        (o especificación estándar) del diseño visual seleccionado.
        Muestra únicamente los campos solicitados por dicho diseño junto con las extensiones esperadas.
        """
        # 1. Guardar cualquier cambio actual que haya introducido el usuario
        for key, edit in self.media_edits.items():
            txt = edit.text().strip()
            if txt:
                self._media_values[key] = txt

        # 2. Reemplazar contenedor dinámico limpiamente
        if hasattr(self, "dynamic_media_container") and self.dynamic_media_container is not None:
            self.dynamic_media_container.setParent(None)
            self.dynamic_media_container.deleteLater()

        self.dynamic_media_container = QWidget()
        dynamic_layout = QFormLayout(self.dynamic_media_container)
        dynamic_layout.setContentsMargins(0, 0, 0, 0)
        dynamic_layout.setSpacing(8)
        self.dynamic_media_wrapper_layout.addWidget(self.dynamic_media_container)

        self.media_edits.clear()

        # 3. Leer especificación del diseño visual actual
        layout_name = self.layout_combo.currentText()
        spec = get_layout_media_spec(layout_name)

        # 4. Crear solo las filas que el diseño requiere
        for item in spec:
            key = item.get("key", "")
            label = item.get("label", key.capitalize())
            folder_name = item.get("folder", key)
            exts = item.get("extensions", [])
            req = item.get("required", False)

            ext_str = ", ".join(exts) if exts else ""
            req_marker = " *" if req else ""
            if ext_str:
                label_text = f"{label} ({ext_str}){req_marker}:"
            else:
                label_text = f"{label}{req_marker}:"

            edit = QLineEdit()
            edit.setPlaceholderText(f"Carpeta de {label} (ej: media/{folder_name})...")
            if key in self._media_values:
                edit.setText(self._media_values[key])

            browse_btn = QPushButton("Examinar…")
            browse_btn.clicked.connect(lambda checked=False, e=edit, l=label: self._pick_media_folder(e, f"Seleccionar carpeta de {l}"))

            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(edit, 1)
            row_layout.addWidget(browse_btn)

            row_widget = QWidget()
            row_widget.setLayout(row_layout)

            dynamic_layout.addRow(label_text, row_widget)
            self.media_edits[key] = edit

    @property
    def boxart_edit(self):
        return self.media_edits.get("boxart")

    @property
    def wheel_edit(self):
        return self.media_edits.get("wheel")

    @property
    def video_edit(self):
        return self.media_edits.get("video")

    @property
    def cartart_edit(self):
        return self.media_edits.get("cartart")

    def _pick_media_folder(self, target_edit, dialog_title):
        current = target_edit.text().strip() or self.media_root_edit.text().strip() or self.folder_edit.text().strip()
        folder = QFileDialog.getExistingDirectory(self, dialog_title, current or "")
        if folder:
            target_edit.setText(folder)
            for k, ed in self.media_edits.items():
                if ed == target_edit:
                    self._media_values[k] = folder

    def pick_media_root(self):
        current = self.media_root_edit.text().strip() or self.folder_edit.text().strip()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta principal de Medios (Media)",
            current or ""
        )
        if folder:
            self.media_root_edit.setText(folder)
            self.auto_detect_media(silent=False)

    def auto_detect_media(self, silent=False):
        base_folder = self.folder_edit.text().strip()
        media_root = self.media_root_edit.text().strip()
        if not base_folder and not media_root:
            if not silent:
                QMessageBox.information(
                    self,
                    "Carpeta requerida",
                    "Seleccioná primero la carpeta de juegos o la de Medios para auto-detectar."
                )
            return

        spec = get_layout_media_spec(self.layout_combo.currentText())
        det = detect_media_folders(base_folder, media_root=media_root, media_spec=spec)
        found_any = False

        if det.get("media_path") and not self.media_root_edit.text().strip():
            self.media_root_edit.setText(det["media_path"])

        for key, edit in self.media_edits.items():
            field = f"{key}_path"
            if field in det and det[field]:
                edit.setText(det[field])
                self._media_values[key] = det[field]
                found_any = True

        if not silent:
            if found_any:
                QMessageBox.information(self, "Medios detectados", "¡Carpetas de medios detectadas y vinculadas exitosamente según el diseño visual!")
            else:
                QMessageBox.information(self, "Búsqueda finalizada", "No se encontraron subcarpetas para los medios requeridos en el directorio.")

    def pick_folder(self):
        current = self.folder_edit.text().strip()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de juegos (ROMs)",
            current or ""
        )
        if folder:
            self.folder_edit.setText(folder)
            self.auto_scan_checkbox.setChecked(True)

            roms_path = Path(folder)
            # Buscar si existe una carpeta de medios en el mismo nivel o subcarpeta
            media_candidate = None
            if (roms_path / "media").is_dir():
                media_candidate = roms_path / "media"
            elif roms_path.parent and (roms_path.parent / "media").is_dir():
                media_candidate = roms_path.parent / "media"
            elif roms_path.name.lower() in ("roms", "games") and roms_path.parent:
                cand = roms_path.parent / "Media"
                if cand.is_dir():
                    media_candidate = cand

            if media_candidate:
                self.media_root_edit.setText(str(media_candidate))
                self.auto_detect_media(silent=True)
            else:
                # Si no está en el mismo nivel o subcarpeta, preguntar al usuario si desea indicar la carpeta Media
                res = QMessageBox.question(
                    self,
                    "Carpeta de Medios no encontrada",
                    "No se detectó una carpeta 'media' en el mismo nivel de la carpeta de juegos.\n\n"
                    "¿Deseas buscar y seleccionar la carpeta de Medios (Media) ahora?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if res == QMessageBox.Yes:
                    self.pick_media_root()
                else:
                    self.auto_detect_media(silent=True)

    def _on_preset_selected(self, index):
        title = self.preset_combo.currentText()
        if title in PRESET_EXTENSIONS and title != "Personalizado...":
            plat, exts = PRESET_EXTENSIONS[title]
            if not self.platform_edit.text().strip():
                self.platform_edit.setText(plat)
            self.extensions_edit.setText(exts)

    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Nombre requerido", "Por favor ingresá un nombre para la lista.")
            self.name_edit.setFocus()
            return

        is_menu = (self.type_combo.currentData() == "menu")
        if is_menu:
            checked_count = sum(1 for i in range(self.sublists_list.count()) if self.sublists_list.item(i).checkState() == Qt.Checked)
            if checked_count == 0:
                answer = QMessageBox.question(
                    self,
                    "Menú sin sistemas",
                    "No seleccionaste ninguna lista para incluir en este menú.\n¿Deseas crearlo de todas formas y vincular sistemas luego?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if answer != QMessageBox.Yes:
                    return
            self.accept()
            return

        raw_exts = self.extensions_edit.text().strip()
        try:
            normalized, warnings = normalize_extensions(raw_exts)
            self.normalized_exts = normalized
        except ValueError as err:
            QMessageBox.warning(
                self,
                "Error en las extensiones",
                f"Configuración de extensiones inválida:\n\n{err}"
            )
            self.extensions_edit.setFocus()
            return

        # Validar carpeta de juegos si fue especificada
        folder = self.folder_edit.text().strip()
        if folder and not Path(folder).is_dir():
            QMessageBox.warning(
                self,
                "Carpeta no encontrada",
                f"La carpeta especificada no existe o no es accesible:\n{folder}\n\nPor favor seleccioná una carpeta válida."
            )
            self.folder_edit.setFocus()
            return

        # Si hay advertencias (ejemplo: extensión genérica .bin)
        if warnings:
            warn_msg = "\n\n".join(warnings)
            answer = QMessageBox.question(
                self,
                "Aviso sobre extensiones configuradas",
                f"{warn_msg}\n\n¿Deseas continuar con esta configuración?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if answer != QMessageBox.Yes:
                return

        self.accept()

    def values(self):
        """Retorna tupla con todos los valores configurados de la lista o menú."""
        list_type = self.type_combo.currentData() if hasattr(self, "type_combo") else "games"
        selected_ids = []
        if list_type == "menu" and hasattr(self, "sublists_list"):
            for i in range(self.sublists_list.count()):
                item = self.sublists_list.item(i)
                if item.checkState() == Qt.Checked:
                    selected_ids.append(item.data(Qt.UserRole))

        # Sincronizar últimos valores de los edits
        for k, ed in self.media_edits.items():
            self._media_values[k] = ed.text().strip()

        media_path = self.media_root_edit.text().strip()
        boxart_path = self._media_values.get("boxart", "")
        wheel_path = self._media_values.get("wheel", "")
        video_path = self._media_values.get("video", "")
        cartart_path = self._media_values.get("cartart", "")

        return (
            self.name_edit.text().strip(),
            self.platform_edit.text().strip(),
            self.emulator_combo.currentData() if list_type == "games" else None,
            self.layout_combo.currentText(),
            self.normalized_exts if list_type == "games" else "",
            self.folder_edit.text().strip() if list_type == "games" else "",
            self.auto_scan_checkbox.isChecked() if list_type == "games" else False,
            media_path,
            boxart_path,
            wheel_path,
            video_path,
            cartart_path,
            list_type,
            selected_ids,
        )



class EmulatorDialog(QDialog):
    """Diálogo para registrar o editar un emulador."""
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Editar emulador" if existing else "Registrar emulador")
        self.setMinimumWidth(560)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Ej: RetroArch, Snes9x, PCSX2, DuckStation...")
        self.exe = QLineEdit()
        self.exe.setPlaceholderText("Ruta al archivo ejecutable (.exe)")
        self.args = QLineEdit('"{rom}"')
        self.platform = QLineEdit()
        self.platform.setPlaceholderText("Ej: Super Nintendo, Multi-sistema...")

        browse = QPushButton("Examinar…")
        browse.clicked.connect(self.pick_exe)

        exe_row = QHBoxLayout()
        exe_row.addWidget(self.exe, 1)
        exe_row.addWidget(browse)

        holder = QWidget()
        holder.setLayout(exe_row)

        form = QFormLayout()
        form.addRow("Nombre del emulador *", self.name)
        form.addRow("Ejecutable (.exe) *", holder)
        form.addRow("Argumentos de inicio", self.args)
        form.addRow("Plataforma (opcional)", self.platform)

        hint = QLabel(
            "<b>Plantillas de argumentos admitidas:</b><br>"
            "<code>{rom}</code> o <code>[romfilename]</code>: Ruta completa al archivo del juego.<br>"
            "<code>{rom_dir}</code> o <code>[rompath]</code>: Carpeta donde se ubica el juego.<br>"
            "<code>{rom_name}</code> o <code>[name]</code>: Nombre del archivo sin extensión.<br>"
            "<i>Ejemplo RetroArch: <code>-f -L cores\\genesis_plus_gx_sot4w_libretro.dll \"{rom}\"</code></i>"
        )
        hint.setStyleSheet("color: #aab1c0; font-size: 9pt;")

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if existing:
            self.name.setText(existing["name"])
            self.exe.setText(existing["executable"])
            self.args.setText(existing["arguments"])
            self.platform.setText(existing["platform"] or "")

    def pick_exe(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar ejecutable del emulador",
            "",
            "Archivos ejecutables (*.exe *.bat *.cmd);;Todos los archivos (*.*)"
        )
        if path:
            self.exe.setText(path)

    def validate_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Dato requerido", "Por favor ingresá un nombre para el emulador.")
            self.name.setFocus()
            return
        if not self.exe.text().strip():
            QMessageBox.warning(self, "Dato requerido", "Por favor seleccioná la ruta al archivo ejecutable.")
            self.exe.setFocus()
            return

        exe_path = Path(self.exe.text().strip())
        if not exe_path.exists():
            confirm = QMessageBox.question(
                self,
                "Ejecutable no encontrado",
                f"El archivo ejecutable no se encuentra actualmente en la ruta indicada:\n{exe_path}\n\n¿Deseas guardarlo de todos modos?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

        self.accept()

    def values(self):
        return (
            self.name.text().strip(),
            self.exe.text().strip(),
            self.args.text().strip() or '"{rom}"',
            self.platform.text().strip()
        )


class EmulatorManagerWidget(QWidget):
    """Panel de administración completa de emuladores para pestaña o ventana."""
    emulators_changed = Signal()

    def __init__(self, db, parent=None, is_dialog=False):
        super().__init__(parent)
        self.db = db
        self.is_dialog = is_dialog
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Encabezado informativo (solo visible en modo pestaña integrada)
        if not self.is_dialog:
            header_card = QFrame()
            header_card.setStyleSheet("background-color: #1b1e2a; border-radius: 8px; padding: 12px;")
            h_layout = QVBoxLayout(header_card)
            title = QLabel("🕹 Administrador de Emuladores")
            title.setFont(QFont("Segoe UI", 16, QFont.Bold))
            title.setStyleSheet("color: #ffffff;")
            h_layout.addWidget(title)

            desc = QLabel(
                "Registrá y administrá los emuladores instalados en tu sistema. "
                "Podés vincular ejecutables, plataformas y parámetros de línea de comandos para cada emulador."
            )
            desc.setStyleSheet("color: #9aa5b8; font-size: 10pt;")
            desc.setWordWrap(True)
            h_layout.addWidget(desc)
            layout.addWidget(header_card)

        # Tabla de emuladores
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Plataforma", "Ejecutable", "Argumentos"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_selected)
        layout.addWidget(self.table, 1)

        # Barra de botones
        btn_row = QHBoxLayout()
        add_btn = QPushButton("＋ Registrar nuevo emulador")
        add_btn.setStyleSheet("background-color: #5d48d9; color: #ffffff; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        add_btn.clicked.connect(self.add_emulator)

        edit_btn = QPushButton("✎ Editar seleccionado")
        edit_btn.clicked.connect(self.edit_selected)

        del_btn = QPushButton("🗑 Eliminar seleccionado")
        del_btn.clicked.connect(self.delete_selected)

        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

    def refresh(self):
        rows = self.db.all("SELECT * FROM emulators ORDER BY name COLLATE NOCASE")
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            name_item = QTableWidgetItem(row["name"])
            name_item.setData(Qt.UserRole, row["id"])
            self.table.setItem(i, 0, name_item)
            self.table.setItem(i, 1, QTableWidgetItem(row["platform"] or "—"))
            self.table.setItem(i, 2, QTableWidgetItem(row["executable"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["arguments"]))

    def _get_selected_id(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        return self.table.item(selected[0].row(), 0).data(Qt.UserRole)

    def add_emulator(self):
        dialog = EmulatorDialog(self)
        if dialog.exec():
            name, exe, args, plat = dialog.values()
            try:
                self.db.execute(
                    "INSERT INTO emulators(name, executable, arguments, platform) VALUES(?,?,?,?)",
                    (name, exe, args, plat)
                )
                self.refresh()
                self.emulators_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error al registrar", f"No se pudo guardar el emulador:\n{e}")

    def edit_selected(self):
        emu_id = self._get_selected_id()
        if not emu_id:
            QMessageBox.information(self, "Seleccionar", "Seleccioná un emulador de la lista para editar.")
            return
        row = self.db.one("SELECT * FROM emulators WHERE id=?", (emu_id,))
        if not row:
            return
        dialog = EmulatorDialog(self, existing=row)
        if dialog.exec():
            name, exe, args, plat = dialog.values()
            try:
                self.db.execute(
                    "UPDATE emulators SET name=?, executable=?, arguments=?, platform=? WHERE id=?",
                    (name, exe, args, plat, emu_id)
                )
                self.refresh()
                self.emulators_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error al actualizar", f"No se pudo actualizar el emulador:\n{e}")

    def delete_selected(self):
        emu_id = self._get_selected_id()
        if not emu_id:
            QMessageBox.information(self, "Seleccionar", "Seleccioná un emulador de la lista para eliminar.")
            return
        row = self.db.one("SELECT name FROM emulators WHERE id=?", (emu_id,))
        if not row:
            return

        # Consultar cuántas listas o juegos usan este emulador
        lists_count = self.db.one("SELECT COUNT(*) AS c FROM game_lists WHERE default_emulator_id=?", (emu_id,))["c"]
        games_count = self.db.one("SELECT COUNT(*) AS c FROM games WHERE emulator_override_id=?", (emu_id,))["c"]

        warning = f"¿Estás seguro de que deseas eliminar el emulador '{row['name']}'?"
        if lists_count > 0 or games_count > 0:
            warning += f"\n\nAtención: Está vinculado a {lists_count} lista(s) y {games_count} juego(s).\nSu asignación pasará a 'Sin emulador'."

        answer = QMessageBox.question(self, "Confirmar eliminación", warning, QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            try:
                self.db.execute("DELETE FROM emulators WHERE id=?", (emu_id,))
                self.refresh()
                self.emulators_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error al eliminar", f"No se pudo eliminar el emulador:\n{e}")


class EmulatorManagerDialog(QDialog):
    """Diálogo completo para administrar (ver, crear, editar, eliminar) emuladores."""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrar emuladores")
        self.resize(780, 480)

        layout = QVBoxLayout(self)
        self.widget = EmulatorManagerWidget(db, self, is_dialog=True)
        layout.addWidget(self.widget)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def refresh(self):
        self.widget.refresh()


class ScanSummaryDialog(QDialog):
    """Diálogo informativo con el resumen completo del escaneo de carpeta."""
    def __init__(self, parent, stats: dict, folder: str, list_name: str, allowed_exts: str):
        super().__init__(parent)
        self.setWindowTitle("Resumen de escaneo de juegos")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        title = QLabel(f"<h2>Escaneo completado para: {list_name}</h2>")
        layout.addWidget(title)

        box = QGroupBox("Detalles de la importación")
        form = QFormLayout(box)
        form.addRow("Carpeta examinada:", QLabel(folder))
        form.addRow("Extensiones permitidas:", QLabel(allowed_exts))
        form.addRow("Archivos coincidentes encontrados:", QLabel(f"<b>{stats['total_found']}</b>"))
        form.addRow("Juegos nuevos agregados:", QLabel(f"<b style='color: #4cd964;'>{stats['added']}</b>"))
        form.addRow("Archivos omitidos (ya existentes):", QLabel(f"<b>{stats['skipped']}</b>"))
        layout.addWidget(box)

        btn = QPushButton("Aceptar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)


class GameEditDialog(QDialog):
    """Diálogo para editar metadatos y configuración individual de un juego."""
    def __init__(self, db, game, parent=None):
        super().__init__(parent)
        self.db = db
        self.game = dict(game) if hasattr(game, "keys") else game
        game = self.game
        self.setWindowTitle(f"Editar juego: {game['title']}")
        self.setMinimumWidth(560)
        self._new_cover_path = None  # Ruta al nuevo archivo de carátula seleccionado

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit(game["title"])
        form.addRow("Título del juego *", self.title_edit)

        self.path_edit = QLineEdit(game["rom_path"])
        browse_btn = QPushButton("Examinar…")
        browse_btn.clicked.connect(self.pick_file)
        path_box = QHBoxLayout()
        path_box.addWidget(self.path_edit, 1)
        path_box.addWidget(browse_btn)
        path_holder = QWidget()
        path_holder.setLayout(path_box)
        form.addRow("Ruta del archivo", path_holder)

        # Carátula / portada del juego
        self.cover_edit = QLineEdit(game.get("cover_path") or "")
        self.cover_edit.setPlaceholderText("Sin carátula asignada (se genera automáticamente)")
        self.cover_edit.setReadOnly(True)
        cover_browse_btn = QPushButton("Elegir imagen…")
        cover_browse_btn.clicked.connect(self.pick_cover)
        cover_clear_btn = QPushButton("✕")
        cover_clear_btn.setToolTip("Quitar carátula asignada (volver a generada automáticamente)")
        cover_clear_btn.setFixedWidth(28)
        cover_clear_btn.clicked.connect(self.clear_cover)
        cover_box = QHBoxLayout()
        cover_box.addWidget(self.cover_edit, 1)
        cover_box.addWidget(cover_browse_btn)
        cover_box.addWidget(cover_clear_btn)
        cover_holder = QWidget()
        cover_holder.setLayout(cover_box)
        form.addRow("Carátula (imagen)", cover_holder)

        cover_hint = QLabel(
            "<i>Formatos admitidos: PNG, JPG, JPEG, BMP, WebP. "
            "La imagen se copia al directorio de carátulas de RetroShelf.</i>"
        )
        cover_hint.setStyleSheet("color: #8a93a8; font-size: 8pt;")
        cover_hint.setWordWrap(True)
        form.addRow("", cover_hint)

        self.override_combo = QComboBox()
        self.override_combo.addItem("Heredar emulador de la lista (por defecto)", None)
        emulators = self.db.all("SELECT * FROM emulators ORDER BY name COLLATE NOCASE")
        for emu in emulators:
            self.override_combo.addItem(f"{emu['name']} ({emu['executable']})", emu["id"])
        idx = self.override_combo.findData(game["emulator_override_id"])
        if idx >= 0:
            self.override_combo.setCurrentIndex(idx)
        form.addRow("Emulador individual", self.override_combo)

        self.args_edit = QLineEdit(game["launch_arguments"] or "")
        self.args_edit.setPlaceholderText("Dejar vacío para usar los argumentos del emulador")
        form.addRow("Argumentos propios", self.args_edit)

        self.notes_edit = QTextEdit(game["notes"] or "")
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Notas", self.notes_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de juego", "", "Todos los archivos (*.*)")
        if path:
            self.path_edit.setText(path)

    def pick_cover(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen de carátula",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp);;Todos los archivos (*.*)"
        )
        if path:
            self._new_cover_path = path
            self.cover_edit.setText(path)

    def clear_cover(self):
        self._new_cover_path = ""  # Cadena vacía = borrar asignación
        self.cover_edit.setText("")

    def save(self):
        title = self.title_edit.text().strip()
        path = self.path_edit.text().strip()
        if not title or not path:
            QMessageBox.warning(self, "Campos requeridos", "El título y la ruta del archivo son obligatorios.")
            return

        emu_override = self.override_combo.currentData()
        args = self.args_edit.text().strip()
        notes = self.notes_edit.toPlainText().strip()

        # Determinar la ruta final de la carátula
        cover_path = self.game.get("cover_path") or ""
        if self._new_cover_path is not None:
            if self._new_cover_path == "":
                # El usuario eligió borrar la carátula
                cover_path = ""
            else:
                # Copiar la imagen al directorio de carátulas
                import shutil
                from retroshelf.ui.cover_utils import get_cover_save_path
                src = Path(self._new_cover_path)
                if src.exists():
                    dest = get_cover_save_path(self.game["id"], src.suffix)
                    try:
                        shutil.copy2(str(src), str(dest))
                        cover_path = str(dest)
                    except Exception as copy_err:
                        QMessageBox.warning(
                            self, "Error al copiar imagen",
                            f"No se pudo copiar la carátula:\n{copy_err}\nSe guardará el resto de los datos."
                        )

        try:
            self.db.execute(
                """UPDATE games SET title=?, rom_path=?, emulator_override_id=?, launch_arguments=?, notes=?, cover_path=?
                   WHERE id=?""",
                (title, path, emu_override, args, notes, cover_path, self.game["id"])
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la información del juego:\n{e}")


RESOLUTIONS_LIST = [
    ("Nativa / Automática (Recomendado)", "native"),
    ("3840 x 2160 (4K Ultra HD - 16:9)", "3840x2160"),
    ("2560 x 1440 (2K QHD - 16:9)", "2560x1440"),
    ("1920 x 1080 (Full HD 1080p - 16:9)", "1920x1080"),
    ("1600 x 900 (HD+ - 16:9)", "1600x900"),
    ("1366 x 768 (Laptop HD - 16:9)", "1366x768"),
    ("1280 x 720 (HD 720p - 16:9)", "1280x720"),
    ("1920 x 1200 (WUXGA - 16:10)", "1920x1200"),
    ("1680 x 1050 (16:10)", "1680x1050"),
    ("1280 x 800 (16:10)", "1280x800"),
    ("1280 x 1024 (SXGA - 5:4)", "1280x1024"),
    ("1024 x 768 (XGA - 4:3)", "1024x768"),
    ("800 x 600 (SVGA - 4:3)", "800x600"),
    ("640 x 480 (VGA - 4:3)", "640x480"),
    ("Personalizada...", "custom"),
]

SCREEN_MODES = [
    ("Pantalla completa (Fullscreen)", "fullscreen"),
    ("Ventana sin bordes (Borderless)", "borderless"),
    ("Modo Ventana (Windowed)", "windowed"),
]


class VideoSettingsDialog(QDialog):
    """
    Diálogo para configurar la resolución, modo de pantalla completa y monitor
    del Frontend / Reproductor de RetroShelf.
    """
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Configuración de Video y Pantalla")
        self.setMinimumWidth(540)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        header = QLabel("<b>Configuración de Video del Frontend</b>")
        header.setStyleSheet("font-size: 11pt; color: #f1f3f9;")
        layout.addWidget(header)

        desc = QLabel(
            "Configurá la resolución, modo de pantalla completa y monitor "
            "con el que se ejecutará el Frontend de juegos (jugar.bat)."
        )
        desc.setStyleSheet("color: #9aa5b8; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(12)

        # 1. Modo de Pantalla
        self.mode_combo = QComboBox()
        for label, val in SCREEN_MODES:
            self.mode_combo.addItem(label, val)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        form.addRow("Modo de pantalla:", self.mode_combo)

        # 2. Resolución
        self.res_combo = QComboBox()
        for label, val in RESOLUTIONS_LIST:
            self.res_combo.addItem(label, val)
        self.res_combo.currentIndexChanged.connect(self._on_res_changed)
        form.addRow("Resolución:", self.res_combo)

        # 3. Resolución personalizada (ancho x alto)
        self.custom_row = QWidget()
        custom_layout = QHBoxLayout(self.custom_row)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(640, 7680)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(480, 4320)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")
        custom_layout.addWidget(QLabel("Ancho:"))
        custom_layout.addWidget(self.width_spin)
        custom_layout.addWidget(QLabel("Alto:"))
        custom_layout.addWidget(self.height_spin)
        form.addRow("Tamaño personalizado:", self.custom_row)
        self.custom_row.setVisible(False)

        # 4. Monitor / Pantalla de destino
        self.screen_combo = QComboBox()
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()
        for idx, scr in enumerate(screens):
            geo = scr.geometry()
            tag = " [Principal]" if scr == primary else ""
            self.screen_combo.addItem(f"Monitor {idx + 1}: {geo.width()}x{geo.height()} ({scr.name()}){tag}", idx)
        self.screen_combo.currentIndexChanged.connect(self._update_info)
        form.addRow("Monitor de destino:", self.screen_combo)

        # 5. Escala de interfaz (UI Scale)
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["100% (Normal)", "125%", "150%", "175%", "200% (4K)"])
        form.addRow("Escala de la interfaz:", self.scale_combo)

        layout.addLayout(form)

        # Nota informativa
        note_box = QGroupBox("Resumen de visualización")
        note_layout = QVBoxLayout(note_box)
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #a0aec0; font-size: 9pt;")
        self.info_label.setWordWrap(True)
        note_layout.addWidget(self.info_label)
        layout.addWidget(note_box)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._load_current_settings()
        self._update_info()

    def _on_mode_changed(self):
        mode = self.mode_combo.currentData()
        # En modo ventana o sin bordes se puede elegir resolución
        self.res_combo.setEnabled(mode != "fullscreen")
        self._update_info()

    def _on_res_changed(self):
        val = self.res_combo.currentData()
        self.custom_row.setVisible(val == "custom")
        self._update_info()

    def _update_info(self):
        mode = self.mode_combo.currentData()
        res = self.res_combo.currentData()
        screens = QGuiApplication.screens()
        s_idx = self.screen_combo.currentIndex()
        cur_screen = screens[s_idx] if 0 <= s_idx < len(screens) else QGuiApplication.primaryScreen()
        geo = cur_screen.geometry() if cur_screen else None
        geo_str = f"{geo.width()}x{geo.height()}" if geo else "pantalla"

        if mode == "fullscreen":
            msg = f"El Frontend iniciará a <b>Pantalla completa</b> ocupando todo el monitor ({geo_str}). Ideal para gabinetes arcade y televisores."
        elif mode == "borderless":
            msg = f"El Frontend iniciará en <b>Ventana sin bordes</b> adaptada a la resolución del monitor ({geo_str})."
        else:
            if res == "native":
                msg = f"Modo <b>Ventana</b> ajustado automáticamente a las dimensiones de la pantalla ({geo_str})."
            elif res == "custom":
                msg = f"Modo <b>Ventana</b> con resolución personalizada de <b>{self.width_spin.value()} x {self.height_spin.value()}</b> píxeles."
            else:
                msg = f"Modo <b>Ventana</b> con resolución fija de <b>{res}</b> píxeles."
        self.info_label.setText(msg)

    def _load_current_settings(self):
        mode = self.db.get_setting("video_mode", "fullscreen")
        idx = self.mode_combo.findData(mode)
        if idx >= 0:
            self.mode_combo.setCurrentIndex(idx)

        res = self.db.get_setting("video_resolution", "native")
        idx_r = self.res_combo.findData(res)
        if idx_r >= 0:
            self.res_combo.setCurrentIndex(idx_r)
        else:
            idx_cust = self.res_combo.findData("custom")
            if idx_cust >= 0:
                self.res_combo.setCurrentIndex(idx_cust)

        self.width_spin.setValue(int(self.db.get_setting("video_custom_width", "1920")))
        self.height_spin.setValue(int(self.db.get_setting("video_custom_height", "1080")))

        mon_idx = int(self.db.get_setting("video_monitor", "0"))
        if 0 <= mon_idx < self.screen_combo.count():
            self.screen_combo.setCurrentIndex(mon_idx)

        scale = self.db.get_setting("video_ui_scale", "100% (Normal)")
        idx_s = self.scale_combo.findText(scale)
        if idx_s >= 0:
            self.scale_combo.setCurrentIndex(idx_s)

        self._on_mode_changed()
        self._on_res_changed()

    def save(self):
        mode = self.mode_combo.currentData()
        res = self.res_combo.currentData()
        self.db.set_setting("video_mode", mode)
        self.db.set_setting("video_resolution", res)
        self.db.set_setting("video_custom_width", str(self.width_spin.value()))
        self.db.set_setting("video_custom_height", str(self.height_spin.value()))
        self.db.set_setting("video_monitor", str(self.screen_combo.currentData()))
        self.db.set_setting("video_ui_scale", self.scale_combo.currentText())
        self.accept()


