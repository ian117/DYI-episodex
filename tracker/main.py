import sys

from PyQt6.QtWidgets import QApplication

from db.database import Database
from services.exporter import Exporter
from services.media_manager import MediaManager
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Episodex")
    app.setApplicationVersion("1.0.0")

    db = Database()
    manager = MediaManager(db)
    exporter = Exporter()

    window = MainWindow(manager, exporter)
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
