#!/usr/bin/env python3
"""Entry point for PSE-Jacobian."""
import sys

from PySide6.QtWidgets import QApplication

from pse_jacobian.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PSE-Jacobian")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
