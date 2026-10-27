import os
from pathlib import Path
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from retroshelf.ui.layouts.base import BaseLayout

class TableLayout(BaseLayout):
    """
    Layout personalizado: Tabla Detallada con datos técnicos ordenables.
    """
    LAYOUT_NAME = "Detalles"
    LAYOUT_DESCRIPTION = "Tabla técnica completa con columnas de tamaño, extensión y emulador"

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._size_cache: dict[str, str] = {}

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Título", "Archivo", "Formato", "Tamaño", "Emulador efectivo"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 180)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.table.itemSelectionChanged.connect(self._on_item_selected)
        self.table.doubleClicked.connect(self._on_double_clicked)
        self.table.itemActivated.connect(self._on_item_activated)
        self.table.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self.table)

    def clear(self):
        super().clear()
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.blockSignals(False)

    def render_games(self):
        self.table.blockSignals(True)
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(self.games))

        for i, g in enumerate(self.games):
            rom_path = g.get("rom_path", "")
            filename = os.path.basename(rom_path)
            _, ext = os.path.splitext(rom_path)

            title_item = QTableWidgetItem(g.get("title", ""))
            title_item.setData(Qt.UserRole, g.get("id"))
            self.table.setItem(i, 0, title_item)

            file_item = QTableWidgetItem(filename)
            file_item.setToolTip(rom_path)
            self.table.setItem(i, 1, file_item)

            self.table.setItem(i, 2, QTableWidgetItem(ext.lower()))

            size_str = self._size_cache.get(rom_path)
            if size_str is None:
                try:
                    st = os.stat(rom_path)
                    mb = st.st_size / (1024 * 1024)
                    size_str = f"{mb:.2f} MB"
                except OSError:
                    size_str = "—"
                self._size_cache[rom_path] = size_str
            self.table.setItem(i, 3, QTableWidgetItem(size_str))

            emu = g.get("effective_name", "Sin emulador")
            source = g.get("source", "")
            source_str = f" ({source})" if source else ""
            self.table.setItem(i, 4, QTableWidgetItem(f"{emu}{source_str}"))

        self.table.setUpdatesEnabled(True)
        self.table.blockSignals(False)

        found = False
        if self.current_game_id:
            found = self.select_game_by_id(self.current_game_id)
        if not found:
            if self.table.rowCount() > 0:
                self.table.blockSignals(True)
                self.table.selectRow(0)
                self.table.blockSignals(False)
                item = self.table.item(0, 0)
                if item:
                    self.current_game_id = item.data(Qt.UserRole)
                    self.game_selected.emit(self.current_game_id)
            else:
                self.current_game_id = None

    def select_game_by_id(self, game_id: int) -> bool:
        self.current_game_id = game_id
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item and item.data(Qt.UserRole) == game_id:
                self.table.blockSignals(True)
                self.table.selectRow(i)
                self.table.blockSignals(False)
                return True
        return False

    def _on_item_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item:
                game_id = item.data(Qt.UserRole)
                if game_id:
                    self.current_game_id = game_id
                    self.game_selected.emit(game_id)
                    return
        rows = self.table.selectionModel().selectedRows()
        if rows:
            item = self.table.item(rows[0].row(), 0)
            if item:
                game_id = item.data(Qt.UserRole)
                if game_id:
                    self.current_game_id = game_id
                    self.game_selected.emit(game_id)

    def _on_item_activated(self, item):
        if item:
            row = item.row()
            id_item = self.table.item(row, 0)
            if id_item:
                game_id = id_item.data(Qt.UserRole)
                if game_id:
                    self.current_game_id = game_id
                    self.game_activated.emit(game_id)

    def _on_double_clicked(self, index=None):
        if self.current_game_id:
            self.game_activated.emit(self.current_game_id)
        elif index and hasattr(index, "isValid") and index.isValid():
            id_item = self.table.item(index.row(), 0)
            if id_item:
                game_id = id_item.data(Qt.UserRole)
                if game_id:
                    self.current_game_id = game_id
                    self.game_activated.emit(game_id)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.current_game_id:
                self.game_activated.emit(self.current_game_id)
                event.accept()
                return
        super().keyPressEvent(event)

    def _on_context_menu(self, pos: QPoint):
        item = self.table.itemAt(pos)
        if item:
            row = item.row()
            self.table.selectRow(row)
            id_item = self.table.item(row, 0)
            if id_item:
                game_id = id_item.data(Qt.UserRole)
                if game_id:
                    self.current_game_id = game_id
                    self.game_selected.emit(game_id)
                    global_pos = self.table.viewport().mapToGlobal(pos)
                    self.context_menu_requested.emit(game_id, global_pos)
