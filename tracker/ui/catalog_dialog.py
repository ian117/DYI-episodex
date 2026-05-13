from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class CatalogDialog(QDialog):
    """Diálogo CRUD genérico para catálogos (tipos, estados, plataformas)."""

    def __init__(
        self,
        window_title: str,
        get_all_fn: Callable[[], list[dict]],
        add_fn: Callable[[str], int],
        rename_fn: Callable[[int, str], None],
        count_fn: Callable[[str], int],
        delete_fn: Callable[[int], None],
        parent=None,
    ):
        super().__init__(parent)
        self._get_all = get_all_fn
        self._add = add_fn
        self._rename = rename_fn
        self._count = count_fn
        self._delete = delete_fn
        self.setWindowTitle(window_title)
        self.setMinimumSize(320, 380)
        self._build_ui()
        self._reload_list()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)

        self._list = QListWidget()
        root.addWidget(self._list, stretch=1)

        btn_layout = QVBoxLayout()
        self._btn_add = QPushButton("Agregar")
        self._btn_rename = QPushButton("Renombrar")
        self._btn_delete = QPushButton("Eliminar")
        btn_layout.addWidget(self._btn_add)
        btn_layout.addWidget(self._btn_rename)
        btn_layout.addWidget(self._btn_delete)
        btn_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        root.addLayout(btn_layout)

        self._btn_add.clicked.connect(self._on_add)
        self._btn_rename.clicked.connect(self._on_rename)
        self._btn_delete.clicked.connect(self._on_delete)

    def _reload_list(self) -> None:
        self._list.clear()
        for entry in self._get_all():
            item = QListWidgetItem(entry['name'])
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self._list.addItem(item)

    def _on_add(self) -> None:
        name, ok = QInputDialog.getText(self, "Nuevo elemento", "Nombre:")
        if not ok or not name.strip():
            return
        existing = [e['name'].lower() for e in self._get_all()]
        if name.strip().lower() in existing:
            QMessageBox.warning(self, "Duplicado", f'"{name.strip()}" ya existe.')
            return
        self._add(name)
        self._reload_list()

    def _on_rename(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        new_name, ok = QInputDialog.getText(
            self, "Renombrar", "Nuevo nombre:", text=entry['name']
        )
        if not ok or not new_name.strip() or new_name.strip() == entry['name']:
            return
        self._rename(entry['id'], new_name)
        self._reload_list()

    def _on_delete(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        count = self._count(entry['name'])

        if count == 0:
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f'¿Eliminar "{entry["name"]}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
        else:
            reply = QMessageBox.warning(
                self,
                "En uso",
                f'"{entry["name"]}" está en uso por {count} título(s).\n\n'
                f'Si lo eliminás, esos títulos conservarán el valor actual '
                f'pero ya no aparecerá en el catálogo.\n\n'
                f'¿Eliminar de todas formas?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

        if reply == QMessageBox.StandardButton.Yes:
            self._delete(entry['id'])
            self._reload_list()
