"""Главный модуль приложения."""

import sys
print("Importing PySide6...")
try:
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication
    print("PySide6 imported OK")
except Exception as e:
    print(f"PySide6 import ERROR: {e}")
    input("Press Enter...")
    sys.exit(1)

print("Importing MainWindow...")
try:
    from piano_ear_trainer.ui.main_window import MainWindow
    print("MainWindow imported OK")
except Exception as e:
    print(f"MainWindow import ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
    sys.exit(1)


def _apply_dark_theme(app: QApplication) -> None:
    """Применяет тёмную тему к приложению."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

    app.setPalette(palette)


def main() -> None:
    """Запуск приложения."""
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        print("QApplication created")
        app.setApplicationName("Piano Ear Trainer")
        _apply_dark_theme(app)
        print("Theme applied")

        window = MainWindow()
        print("MainWindow created")
        window.show()
        print("Window shown, entering event loop...")

        sys.exit(app.exec())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


print(f"__name__ = {__name__}")
if __name__ == "__main__":
    print("Calling main()...")
    main()
else:
    print("Not __main__, exiting...")
    input("Press Enter...")
