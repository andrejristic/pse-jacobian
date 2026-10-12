"""Single entry point for the packaged app: launches the GUI."""
import sys
from PySide6.QtWidgets import QApplication
from pse_jacobian.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PSE-Jacobian")
    MainWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
