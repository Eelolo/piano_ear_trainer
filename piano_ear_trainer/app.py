"""Главный модуль приложения."""

import sys

from PySide6.QtWidgets import QApplication

from piano_ear_trainer.ui.main_window import MainWindow


def main() -> None:
    """Запуск приложения."""
    app = QApplication(sys.argv)
    app.setApplicationName("Piano Ear Trainer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
