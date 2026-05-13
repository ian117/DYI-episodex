from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.title import Title
from services.exporter import Exporter
from services.media_manager import MediaManager
from ui.catalog_dialog import CatalogDialog
from ui.detail_view import DetailView
from ui.form_dialog import FormDialog


class MainWindow(QMainWindow):
    def __init__(self, manager: MediaManager, exporter: Exporter):
        super().__init__()
        self._manager = manager
        self._exporter = exporter
        self.setWindowTitle("Episodex")
        self.setMinimumSize(960, 560)
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        # ── Barra de búsqueda y filtros ──
        filter_bar = QHBoxLayout()

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Buscar por nombre…")
        filter_bar.addWidget(self._search_edit, stretch=2)

        self._filter_type = QComboBox()
        self._filter_type.addItem("Todos los tipos", "")
        for t in self._manager.get_types():
            self._filter_type.addItem(t, t)
        filter_bar.addWidget(QLabel("Tipo:"))
        filter_bar.addWidget(self._filter_type)

        self._filter_status = QComboBox()
        self._filter_status.addItem("Todos los estados", "")
        for s in self._manager.get_statuses():
            self._filter_status.addItem(s, s)
        filter_bar.addWidget(QLabel("Estado:"))
        filter_bar.addWidget(self._filter_status)

        self._filter_platform = QComboBox()
        self._filter_platform.addItem("Todas las plataformas", "")
        for p in self._manager.get_platforms():
            self._filter_platform.addItem(p, p)
        filter_bar.addWidget(QLabel("Plataforma:"))
        filter_bar.addWidget(self._filter_platform)

        btn_clear = QPushButton("Limpiar filtros")
        btn_clear.clicked.connect(self._clear_filters)
        filter_bar.addWidget(btn_clear)

        root.addLayout(filter_bar)

        # ── Tabla principal ──
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Título", "Tipo", "Temporada", "Episodio", "Estado", "Valoración", "Plataforma"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self._open_detail_view)
        root.addWidget(self.table)

        # ── Barra de acciones ──
        action_bar = QHBoxLayout()
        self._btn_add = QPushButton("Agregar")
        self._btn_edit = QPushButton("Editar")
        self._btn_detail = QPushButton("Ver detalle")
        self._btn_delete = QPushButton("Eliminar")
        self._btn_export = QPushButton("Exportar")
        self._btn_import = QPushButton("Importar")
        self._btn_types = QPushButton("Tipos")
        self._btn_statuses = QPushButton("Estados")
        self._btn_platforms = QPushButton("Plataformas")

        for btn in (self._btn_add, self._btn_edit, self._btn_detail, self._btn_delete,
                    self._btn_export, self._btn_import, self._btn_types,
                    self._btn_statuses, self._btn_platforms):
            action_bar.addWidget(btn)

        self._btn_add.clicked.connect(self._open_add_dialog)
        self._btn_edit.clicked.connect(self._open_edit_dialog)
        self._btn_detail.clicked.connect(self._open_detail_view)
        self._btn_delete.clicked.connect(self._delete_selected)
        self._btn_export.clicked.connect(self._export_dialog)
        self._btn_import.clicked.connect(self._import_dialog)
        self._btn_types.clicked.connect(self._open_types_dialog)
        self._btn_statuses.clicked.connect(self._open_statuses_dialog)
        self._btn_platforms.clicked.connect(self._open_platforms_dialog)

        root.addLayout(action_bar)

        # ── Debounce para búsqueda ──
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_edit.textChanged.connect(self._search_timer.start)
        self._search_timer.timeout.connect(self._refresh_table)

        self._filter_type.currentIndexChanged.connect(self._refresh_table)
        self._filter_status.currentIndexChanged.connect(self._refresh_table)
        self._filter_platform.currentIndexChanged.connect(self._refresh_table)

    # ── Lógica de tabla ──────────────────────────────────────────────────────

    def _refresh_table(self) -> None:
        search_text = self._search_edit.text().strip()
        if search_text:
            titles = self._manager.search(search_text)
            titles = self._apply_filters_locally(titles)
        else:
            titles = self._manager.get_all(self._build_filters())
        self._populate_table(titles)

    def _build_filters(self) -> dict:
        filters = {}
        type_val = self._filter_type.currentData()
        status_val = self._filter_status.currentData()
        platform_val = self._filter_platform.currentData()
        if type_val:
            filters['type'] = type_val
        if status_val:
            filters['status'] = status_val
        if platform_val:
            filters['platform'] = platform_val
        return filters

    def _apply_filters_locally(self, titles: list[Title]) -> list[Title]:
        type_val = self._filter_type.currentData()
        status_val = self._filter_status.currentData()
        platform_val = self._filter_platform.currentData()
        if type_val:
            titles = [t for t in titles if t.type == type_val]
        if status_val:
            titles = [t for t in titles if t.status == status_val]
        if platform_val:
            titles = [t for t in titles if t.platform == platform_val]
        return titles

    def _populate_table(self, titles: list[Title]) -> None:
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(titles))

        for row_idx, t in enumerate(titles):
            items = [
                QTableWidgetItem(t.title),
                QTableWidgetItem(t.type),
                QTableWidgetItem(str(t.season) if t.season is not None else "—"),
                QTableWidgetItem(str(t.episode) if t.episode is not None else "—"),
                QTableWidgetItem(t.status),
                QTableWidgetItem(f"★ {t.rating}" if t.rating else "—"),
                QTableWidgetItem(t.platform or "—"),
            ]
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col, item)

            self.table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, t.id)

        self.table.setSortingEnabled(True)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _clear_filters(self) -> None:
        self._search_edit.clear()
        self._filter_type.setCurrentIndex(0)
        self._filter_status.setCurrentIndex(0)
        self._filter_platform.setCurrentIndex(0)

    # ── Acciones sobre títulos ───────────────────────────────────────────────

    def _open_add_dialog(self) -> None:
        dialog = FormDialog(
            self._manager.get_types(),
            self._manager.get_statuses(),
            self._manager.get_platforms(),
            parent=self,
        )
        if dialog.exec():
            self._manager.add(dialog.get_title())
            self._refresh_table()

    def _open_edit_dialog(self, title_id: int = None) -> None:
        if title_id is None:
            title_id = self._selected_id()
        if title_id is None:
            return
        title = self._manager.get_by_id(title_id)
        if not title:
            return
        dialog = FormDialog(
            self._manager.get_types(),
            self._manager.get_statuses(),
            self._manager.get_platforms(),
            title=title,
            parent=self,
        )
        if dialog.exec():
            self._manager.update(dialog.get_title())
            self._refresh_table()

    def _open_detail_view(self) -> None:
        title_id = self._selected_id()
        if title_id is None:
            return
        title = self._manager.get_by_id(title_id)
        if not title:
            return
        detail = DetailView(title, parent=self)
        detail.edit_requested.connect(self._open_edit_dialog)
        detail.exec()

    def _delete_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        title_name = self.table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f'¿Eliminar "{title_name}"? Esta acción no se puede deshacer.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            title_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self._manager.delete(title_id)
            self._refresh_table()

    def _import_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar biblioteca",
            "",
            "CSV y JSON (*.csv *.json);;CSV (*.csv);;JSON (*.json)",
        )
        if not path:
            return

        try:
            if path.endswith('.csv'):
                candidates = self._exporter.from_csv(path)
            else:
                candidates = self._exporter.from_json(path)
        except Exception as e:
            QMessageBox.critical(self, "Error al importar", f"No se pudo leer el archivo:\n{e}")
            return

        # Sincronizar catálogos con valores nuevos del archivo
        known_types = {v.lower() for v in self._manager.get_types()}
        known_statuses = {v.lower() for v in self._manager.get_statuses()}
        known_platforms = {v.lower() for v in self._manager.get_platforms()}
        catalogs_changed = False

        for t in candidates:
            if t.type and t.type.lower() not in known_types:
                self._manager.add_type(t.type)
                known_types.add(t.type.lower())
                catalogs_changed = True
            if t.status and t.status.lower() not in known_statuses:
                self._manager.add_status(t.status)
                known_statuses.add(t.status.lower())
                catalogs_changed = True
            if t.platform and t.platform.lower() not in known_platforms:
                self._manager.add_platform(t.platform)
                known_platforms.add(t.platform.lower())
                catalogs_changed = True

        if catalogs_changed:
            self._refresh_type_filter()
            self._refresh_status_filter()
            self._refresh_platform_filter()

        existing = {t.title.lower() for t in self._manager.get_all()}
        imported = skipped = 0
        for t in candidates:
            if not t.title:
                continue
            if t.title.lower() in existing:
                skipped += 1
            else:
                self._manager.add(t)
                existing.add(t.title.lower())
                imported += 1

        self._refresh_table()
        partes = []
        if imported:
            partes.append(f"{imported} título(s) importado(s)")
        if skipped:
            partes.append(f"{skipped} omitido(s) por nombre duplicado")
        QMessageBox.information(self, "Importación completada", ".\n".join(partes) + ".")

    def _export_dialog(self) -> None:
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar biblioteca",
            "",
            "CSV (*.csv);;JSON (*.json)",
        )
        if not path:
            return
        titles = self._manager.get_all()
        if "CSV" in selected_filter:
            if not path.endswith('.csv'):
                path += '.csv'
            self._exporter.to_csv(titles, path)
        else:
            if not path.endswith('.json'):
                path += '.json'
            self._exporter.to_json(titles, path)
        QMessageBox.information(self, "Exportación completada", f"Archivo guardado en:\n{path}")

    # ── Gestión de catálogos ─────────────────────────────────────────────────

    def _open_types_dialog(self) -> None:
        m = self._manager
        CatalogDialog(
            "Gestionar tipos",
            m.get_types_full, m.add_type, m.rename_type,
            m.count_titles_with_type, m.delete_type,
            parent=self,
        ).exec()
        self._refresh_type_filter()

    def _open_statuses_dialog(self) -> None:
        m = self._manager
        CatalogDialog(
            "Gestionar estados",
            m.get_statuses_full, m.add_status, m.rename_status,
            m.count_titles_with_status, m.delete_status,
            parent=self,
        ).exec()
        self._refresh_status_filter()

    def _open_platforms_dialog(self) -> None:
        m = self._manager
        CatalogDialog(
            "Gestionar plataformas",
            m.get_platforms_full, m.add_platform, m.rename_platform,
            m.count_titles_with_platform, m.delete_platform,
            parent=self,
        ).exec()
        self._refresh_platform_filter()

    def _refresh_type_filter(self) -> None:
        self._filter_type.blockSignals(True)
        self._filter_type.clear()
        self._filter_type.addItem("Todos los tipos", "")
        for t in self._manager.get_types():
            self._filter_type.addItem(t, t)
        self._filter_type.blockSignals(False)

    def _refresh_status_filter(self) -> None:
        self._filter_status.blockSignals(True)
        self._filter_status.clear()
        self._filter_status.addItem("Todos los estados", "")
        for s in self._manager.get_statuses():
            self._filter_status.addItem(s, s)
        self._filter_status.blockSignals(False)

    def _refresh_platform_filter(self) -> None:
        self._filter_platform.blockSignals(True)
        self._filter_platform.clear()
        self._filter_platform.addItem("Todas las plataformas", "")
        for p in self._manager.get_platforms():
            self._filter_platform.addItem(p, p)
        self._filter_platform.blockSignals(False)
