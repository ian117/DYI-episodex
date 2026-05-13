from typing import Optional

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
)

from models.title import Title


class FormDialog(QDialog):
    def __init__(
        self,
        types: list[str],
        statuses: list[str],
        platforms: list[str],
        title: Optional[Title] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._title_id = title.id if title else None
        self._build_ui(types, statuses, platforms)
        if title:
            self._populate(title)
        self.setWindowTitle("Editar título" if title else "Agregar título")
        self.setMinimumWidth(400)

    def _build_ui(self, types: list[str], statuses: list[str], platforms: list[str]) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        form.addRow("Título *", self.title_edit)

        self.type_combo = QComboBox()
        for t in types:
            self.type_combo.addItem(t)
        form.addRow("Tipo *", self.type_combo)

        self.season_spin = QSpinBox()
        self.season_spin.setRange(0, 999)
        form.addRow("Temporada", self.season_spin)

        self.episode_spin = QSpinBox()
        self.episode_spin.setRange(0, 9999)
        form.addRow("Episodio", self.episode_spin)

        self.status_combo = QComboBox()
        for s in statuses:
            self.status_combo.addItem(s)
        form.addRow("Estado *", self.status_combo)

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(0, 10)
        self.rating_spin.setSpecialValueText("Sin valoración")
        form.addRow("Valoración (0=ninguna)", self.rating_spin)

        self.platform_combo = QComboBox()
        self.platform_combo.addItem("— Sin plataforma —", "")
        for p in platforms:
            self.platform_combo.addItem(p, p)
        form.addRow("Plataforma", self.platform_combo)

        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Notas", self.notes_edit)

        self.date_check = QCheckBox("Registrar fecha de visionado")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setEnabled(False)
        form.addRow(self.date_check)
        form.addRow("Fecha (YYYY-MM-DD)", self.date_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.date_check.toggled.connect(self.date_edit.setEnabled)

    def _populate(self, t: Title) -> None:
        self.title_edit.setText(t.title)

        idx = self.type_combo.findText(t.type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)

        if t.season is not None:
            self.season_spin.setValue(t.season)
        if t.episode is not None:
            self.episode_spin.setValue(t.episode)

        idx = self.status_combo.findText(t.status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        self.rating_spin.setValue(t.rating if t.rating else 0)

        idx = self.platform_combo.findData(t.platform or "")
        if idx >= 0:
            self.platform_combo.setCurrentIndex(idx)

        if t.notes:
            self.notes_edit.setPlainText(t.notes)

        if t.watched_at:
            date = QDate.fromString(t.watched_at, "yyyy-MM-dd")
            if date.isValid():
                self.date_edit.setDate(date)
                self.date_check.setChecked(True)

    def _validate_and_accept(self) -> None:
        if not self.title_edit.text().strip():
            self.title_edit.setFocus()
            return
        self.accept()

    def get_title(self) -> Title:
        rating = self.rating_spin.value()
        platform = self.platform_combo.currentData()

        watched_at = None
        if self.date_check.isChecked():
            watched_at = self.date_edit.date().toString("yyyy-MM-dd")

        return Title(
            id=self._title_id,
            title=self.title_edit.text().strip(),
            type=self.type_combo.currentText(),
            status=self.status_combo.currentText(),
            season=self.season_spin.value() or None,
            episode=self.episode_spin.value() or None,
            rating=rating if rating > 0 else None,
            platform=platform if platform else None,
            notes=self.notes_edit.toPlainText().strip() or None,
            watched_at=watched_at,
        )
