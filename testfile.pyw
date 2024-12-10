import os
import sys
# json 사용을 위한 패키지
import json
# 핫키 사용을 위한 패키지
import keyboard
import pyautogui
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, 
                             QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
# 파일명에 타임스탬프(년월일시분초 표기)를 위해 사용한 패키지
from datetime import datetime

# Qt 플랫폼 플러그인 경로를 명시적으로 설정, 오류가 없을 시 사용하지 않는 코드
'''
qt_plugin_path = r"C:\Users\신동희\AppData\Local\Programs\Python\Python313\Lib\site-packages\PyQt5\Qt5\plugins"
os.environ["QT_PLUGIN_PATH"] = qt_plugin_path
'''

# class로 코드를 묶어 관리하기 쉽게 작성,
class ScreenshotThread(QThread):
    screenshot_taken = pyqtSignal(str)

    def __init__(self, save_path):
        super().__init__()
        self.save_path = save_path

    def run(self):
        try:
            # 스크린샷 찍기
            screenshot = pyautogui.screenshot()
            
            # 파일 이름 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # 저장 경로 생성
            full_path = os.path.join(os.path.dirname(self.save_path), filename)
            
            # 스크린샷 저장
            screenshot.save(full_path)
            
            # 스크린샷 저장 경로 신호 전송
            self.screenshot_taken.emit(full_path)
        except Exception as e:
            # 오류 메시지 신호 전송
            self.screenshot_taken.emit(f"Error: {str(e)}")


class SettingsWindow(QWidget):
    def __init__(self, screenshot_app=None):
        super().__init__()
        self.screenshot_app = screenshot_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Hotkey Input
        layout.addWidget(QLabel("Screen Capture key:"))
        self.hotkey_input = QLineEdit(self.screenshot_app.hotkey)
        layout.addWidget(self.hotkey_input)
        
        # Save Path Input
        layout.addWidget(QLabel("Save Folder:"))
        self.save_path_input = QLineEdit(self.screenshot_app.save_path)
        layout.addWidget(self.save_path_input)
        
        self.save_path_button = QPushButton("Fold Browse")
        self.save_path_button.clicked.connect(self.browse_save_path)
        layout.addWidget(self.save_path_button)
        
        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.setWindowTitle("SCOP")
        self.setGeometry(300, 300, 400, 200)

    def browse_save_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Save Path", 
            self.screenshot_app.save_path, 
            "Images (*.png)"
        )
        if path:
            self.save_path_input.setText(path)

    def save_settings(self):
        new_hotkey = self.hotkey_input.text()
        new_save_path = self.save_path_input.text()

        # 스크린샷 앱에 설정 전달
        if self.screenshot_app:
            self.screenshot_app.update_settings(new_hotkey, new_save_path)
        
        # 창을 닫는 대신 숨기기
        self.hide()

        # 저장 완료 메시지 표시
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")


class ScreenshotApp:
    SETTINGS_FILE = "settings.json"  # 설정 파일 경로

    def __init__(self, app):
        self.app = app
        self.hotkey = 'ctrl+alt+c'
        self.save_path = os.path.expanduser("~/Desktop/screenshot.png")
        self.icon_path = "camera-photo.ico"  # 기본 아이콘 경로
        
        # 설정 파일에서 읽기
        self.load_settings()
        
        self.settings_window = SettingsWindow(self)
        
        # 시스템 트레이 아이콘 설정
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path))
        
        # 트레이 메뉴 생성
        tray_menu = QMenu()
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 핫키 등록
        self.register_hotkey()

    def load_settings(self):
        """설정 파일에서 읽기"""
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r") as file:
                    settings = json.load(file)
                    self.hotkey = settings.get("hotkey", self.hotkey)
                    self.save_path = settings.get("save_path", self.save_path)
                    self.icon_path = settings.get("icon_path", self.icon_path)
            except Exception as e:
                QMessageBox.warning(None, "Settings Error", f"Failed to load settings: {e}")

    def save_settings_to_file(self):
        """설정을 파일에 저장"""
        try:
            settings = {
                "hotkey": self.hotkey,
                "save_path": self.save_path,
                "icon_path": self.icon_path
            }
            with open(self.SETTINGS_FILE, "w") as file:
                json.dump(settings, file, indent=4)
        except Exception as e:
            QMessageBox.warning(None, "Settings Error", f"Failed to save settings: {e}")

    def update_settings(self, hotkey, save_path):
        self.hotkey = hotkey
        self.save_path = save_path
        
        # 핫키 재등록
        self.register_hotkey()
        
        # 설정 파일에 저장
        self.save_settings_to_file()

    def register_hotkey(self):
        try:
            # 기존 핫키 해제
            keyboard.unhook_all()
            
            # 새 핫키 등록
            keyboard.add_hotkey(self.hotkey, self.start_screenshot_thread)
        except Exception as e:
            QMessageBox.warning(None, "Hotkey Error", f"Could not register hotkey: {str(e)}")

    def start_screenshot_thread(self):
        self.screenshot_thread = ScreenshotThread(self.save_path)
        self.screenshot_thread.screenshot_taken.connect(self.handle_screenshot_result)
        self.screenshot_thread.start()

    def handle_screenshot_result(self, result):
        if result.startswith("Error"):
            self.tray_icon.showMessage("Screenshot Error", result, QSystemTrayIcon.Warning, 3000)
        else:
            self.tray_icon.showMessage("Screenshot", f"Saved to {result}", QSystemTrayIcon.Information, 3000)

    def show_settings(self):
        # 현재 설정으로 설정 창 초기화
        self.settings_window.hotkey_input.setText(self.hotkey)
        self.settings_window.save_path_input.setText(self.save_path)
        self.settings_window.show()

    def exit_application(self):
        reply = QMessageBox.question(
            None, "Exit", "Are you sure you want to exit?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.app.quit()


def main():
    app = QApplication(sys.argv)
    screenshot_app = ScreenshotApp(app)
    app.aboutToQuit.connect(screenshot_app.save_settings_to_file)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
