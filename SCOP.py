import sys
import os
import keyboard
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QGuiApplication
from PIL import ImageGrab


class CaptureWindow(QWidget):
    def __init__(self, save_path):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.save_path = save_path
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.4)
        self.setCursor(Qt.CrossCursor)
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()

    def mousePressEvent(self, event):
        self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.capture_screen()
        self.close()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()
        self.update()

    def paintEvent(self, event):
        if self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.drawRect(QRect(self.start_pos, self.end_pos))

    def capture_screen(self):
        x1 = min(self.start_pos.x(), self.end_pos.x())
        y1 = min(self.start_pos.y(), self.end_pos.y())
        x2 = max(self.start_pos.x(), self.end_pos.x())
        y2 = max(self.start_pos.y(), self.end_pos.y())

        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, x1, y1, x2 - x1, y2 - y1)
        screenshot.save(self.save_path)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hotkey = 'ctrl+alt+c'
        self.save_path = os.path.expanduser("~/Desktop/screenshot.png")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Hotkey Input
        layout.addWidget(QLabel("Capture Hotkey:"))
        self.hotkey_input = QLineEdit(self.hotkey)
        layout.addWidget(self.hotkey_input)

        # Save Path Input
        layout.addWidget(QLabel("Save Path:"))
        self.save_path_input = QLineEdit(self.save_path)
        layout.addWidget(self.save_path_input)
        self.save_path_button = QPushButton("Browse")
        self.save_path_button.clicked.connect(self.browse_save_path)
        layout.addWidget(self.save_path_button)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 200)

    def browse_save_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Save Path", self.save_path, "Images (*.png *.jpg *.bmp)")
        if path:
            self.save_path_input.setText(path)

    def save_settings(self):
        self.hotkey = self.hotkey_input.text()
        self.save_path = self.save_path_input.text()
        self.close()
        start_background_capture(self.hotkey, self.save_path)


def start_background_capture(hotkey, save_path):
    def trigger_capture():
        app = QApplication(sys.argv)
        capture_window = CaptureWindow(save_path)
        app.exec_()

    keyboard.add_hotkey(hotkey, trigger_capture)
    print(f"Background capture started. Press {hotkey} to capture the screen.")
    print(f"Images will be saved to: {save_path}")

    # Keeps the script running
    keyboard.wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())