from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from models.title import Title


class DetailView(QDialog):
    edit_requested = pyqtSignal(int)

    def __init__(self, title: Title, parent=None):
        super().__init__(parent)
        self._title = title
        self.setWindowTitle(title.title)
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self) -> None:
        t = self._title
        layout = QVBoxLayout(self)
        form = QFormLayout()

        form.addRow("Título:", QLabel(t.title))
        form.addRow("Tipo:", QLabel(t.type))

        season_str = str(t.season) if t.season is not None else "—"
        episode_str = str(t.episode) if t.episode is not None else "—"
        form.addRow("Temporada:", QLabel(season_str))
        form.addRow("Episodio:", QLabel(episode_str))

        form.addRow("Estado:", QLabel(t.status))

        rating_str = f"★ {t.rating} / 10" if t.rating else "Sin valoración"
        form.addRow("Valoración:", QLabel(rating_str))

        form.addRow("Plataforma:", QLabel(t.platform or "—"))
        form.addRow("Fecha visionado:", QLabel(t.watched_at or "—"))

        notes_label = QLabel(t.notes or "—")
        notes_label.setWordWrap(True)
        form.addRow("Notas:", notes_label)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_edit = QPushButton("Editar")
        btn_close = QPushButton("Cerrar")
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        btn_edit.clicked.connect(self._on_edit)
        btn_close.clicked.connect(self.accept)

    def _on_edit(self) -> None:
        self.edit_requested.emit(self._title.id)
        self.accept()
