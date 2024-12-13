# 필요한 패키지를 import 하는 부분

# 운영체제와의 상호 작용을 위한 패키지
import os
# 시스템과 관련된 기능, 코드들을 사용하기 위한 패키지
import sys
# JSON에 설정을 저장하고 불러오기 기능을 사용하기 위한 패키지
import json
# 키보드의 입력을 받고 처리하는 기능을 위한 패키지
import keyboard
# 스크린샷 기능을 사용하기 위해 가져온 패키지
import pyautogui
# PyQt5 패키지에서 GUI를 구성하기 위한 요소들을 가져오는 부분
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, 
    QSystemTrayIcon, QMenu
)
# 프로그램에서 백그라운드 상시 작동을 위한 트레이 아이콘을 설정하기 위한 패키지
from PyQt5.QtGui import QIcon
# Thread 및 신호를 처리하기 위한 패키지
from PyQt5.QtCore import QThread, pyqtSignal, Qt
# 파일명에 넣어줄 시간 정보를 만들기 위한 패키지
from datetime import datetime

# Qt 플러그인의 경로를 명시(일부 환경에선 미지정시 오류가 발생하여 PyQt5가 작동하도록 환경 변수 설정)
# 아래와 같은 코드에서 C:\~~~ 와 같은 Qt 플러그인의 위치를 찾아 직접 경로를 입력하면 된다.
'''qt_plugin_path = r"C:\Users\신동희\AppData\Local\Programs\Python\Python313\Lib\site-packages\PyQt5\Qt5\plugins"
os.environ["QT_PLUGIN_PATH"] = qt_plugin_path'''

# 코드가 눈에 잘 보이게 하기 위해 나눈 클래스
# 1. 스크린샷을 찍는 작업을 백그라운드에서 처리하는 과정
class ScreenshotThread(QThread):

    # 스크린샷을 완료했을 경우, 경로를 전달하는 부분
    screenshot_taken = pyqtSignal(str)

    # 저장 경로를 초기화하는 부분
    def __init__(self, save_path):
        super().__init__()
        self.save_path = save_path

    # 해당되는 Thread가 실행 될 경우 작동하는 함수
    def run(self):
        try:
            # 현재 켜져있는 화면의 스크린샷을 찍는다.
            screenshot = pyautogui.screenshot()
            
            # datetime.now를 통하여 년월일_시분초에 해당하는 이름을 만들어 타임스탬프에 저장한다.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 파일명에 screenshot_(타임스탬프에 해당하는 값).png를 지정한다.
            filename = f"screenshot_{timestamp}.png"
            
            # 전체적인 저장 경로를 생성한다
            full_path = os.path.join(os.path.dirname(self.save_path), filename)
            
            # 스크린샷을 저장하는 코드이다.
            screenshot.save(full_path)
            
            # 저장된 경로를 신호로 전달하는 코드이다.
            self.screenshot_taken.emit(full_path)

        #예외 경우
        except Exception as e:
            # 만약 예상치 못한 오류가 발생 시, 저장된 경로를 신호로 보내는 것이 아닌, 에러 메시지를 전달한다.
            self.screenshot_taken.emit(f"Error: {str(e)}")

# 2. 해당 클래스는 설정창을 구현하기 위한 클래스이다.
class SettingsWindow(QWidget):
    def __init__(self, screenshot_app=None):
        # 다른 클래스의 속성 및 메소드를 자동으로 불러와 해당 클래스에서도 사용이 가능하도록 해주는 부분.
        super().__init__()
        # 메인 애플리케이션과 연결을 위한 코드
        self.screenshot_app = screenshot_app
        # 기본적으로, 창을 닫으면 프로그램은 강제 종료되지만, 해당 코드를 통해 종료를 막는다.,
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        # UI를 초기화 한다.
        self.init_ui()

    #UI 설정을 위한 부분
    def init_ui(self):
        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # 스크린샷 핫키를 지정하기 위한 위젯 생성 코드
        # Screenshot Hotkey의 레이블을 추가한다.
        layout.addWidget(QLabel("Screenshot Hotkey:"))
        # 현재 세팅되어 있는 핫키의 값이 무엇인지 표기하여준다.
        self.hotkey_input = QLineEdit(self.screenshot_app.hotkey)
        # UI 레이아웃에 위젯(입력하는 상자)을 추가하는 부분이다.
        layout.addWidget(self.hotkey_input)
        
        # 저장 경로 입력을 위한 코드
        # 저장 경로를 지정하기 위한 레이블을 추가한다.
        layout.addWidget(QLabel("Save Folder:"))
        # 현재 지정되어있는 저장 경로의 값이 무엇인지 표기하여 준다.
        self.save_path_input = QLineEdit(self.screenshot_app.save_path)
        # UI 레이아웃에 위젯(입력하는 상자)을 추가하는 부분이다.
        layout.addWidget(self.save_path_input)
        
        # 저장 경로 탐색 버튼을 위한 코드
        # Open Save Path의 버튼을 추가한다.
        self.save_path_button = QPushButton("Open Save Path")
        # Open Save Path가 적힌 버튼을 누를 시, 직접 경로를 지정할 수 있는 창을 열어준다.
        self.save_path_button.clicked.connect(self.browse_save_path)
        # UI 레이아웃에 위젯(클릭할 수 있는 버튼)을 추가하는 부분이다.
        layout.addWidget(self.save_path_button)
        
        # 설정 저장 버튼을 만들기 위한 코드
        # Save Settings인 버튼을 추가한다.
        self.save_button = QPushButton("Save Settings")
        # Save Settings 버튼 클릭시 현재 UI에서 지정되었던 설정을 저장
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
        # 레이아웃 설정을 위한 코드
        self.setLayout(layout)
        # 켜져있는 UI의 프로그램 제목을 설정한다. 코드에서는 SCOP Settings UI로 지정하였다.
        self.setWindowTitle("SCOP Settings UI")
        # 창의 크기와 위치를 지정해주었다.
        self.setGeometry(300, 300, 400, 200)

    # 저장 경로를 탐색하기 위한 코드(Open Save Path와 연결이 되는 부분이다)
    def browse_save_path(self):

        # 저장 경로를 탐색하게 도와주는 다이얼로그 창을 오픈하는 코드
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Save Path", # 다이얼로그로 열린 창에 Select Save Path라는 제목을 넣는다.
            self.screenshot_app.save_path, 
            "image names (*.png)" # 다이얼로그로 열린 창에 image names (*.png)라는 내용을 넣어 가이드해준다.
        )
        # 만약, 경로가 설정되었을 경우
        if path:
        # Save Path에 해당 경로를 표기하는 코드이다
            self.save_path_input.setText(path)

    # Save Settings 버튼 클릭시 호출되는 코드이다.
    def save_settings(self):
        # 뉴 핫키 변수에 입력되어 있는 핫키를 가져온다.
        new_hotkey = self.hotkey_input.text()
        # 새로운 저장 경로 변수에 입력되어 있는 저장 경로 가져오기
        new_save_path = self.save_path_input.text()

        # 메인 어플리케이션의 설정을 반영하는 부분
        if self.screenshot_app:
            # 새로운 핫키와 저장경로를 반영한다.
            self.screenshot_app.update_settings(new_hotkey, new_save_path)
        
        # 저장이 정상적으로 완료되었는지 확인하기 위해 팝업 알림으로 저장이 성공적으로 완료되었다는 것을 안내한다.
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        
        # 저장이 완료되었으니 창을 숨기는 코드이다.
        self.hide()

    # 창 닫기 요청이 들어왔을 때 프로그램을 종료시키지 않기 위한 방지용 코드이다. 프로그램 종료가 아닌, 창을 숨기는 방식이다.
    def closeEvent(self, event):
        # 닫기 요청이 들어와도 요청을 무시한다.
        event.ignore()
        # 그리고 창을 숨겨 종료된 것 처럼 보이게 한다.
        self.hide()

# 스크린샷 애플리케이션의 메인 클래스를 나타내는 부분이다.
class ScreenshotApp:
    # 설정을 저장할 파일의 이름을 지정한 부분이다.
    SETTINGS_FILE = "settings.json"

    def __init__(self, app):
        self.app = app  # QApplication 객체
        # 프로그램 처음 시작 시, 기본으로 지정해둔 핫키이다, 기본적으로는 settings.json에서 불러올 예정이기 때문에 의미는 크게 없다.
        self.hotkey = 'ctrl+alt+c'
        # 기본으로 지정된 저장 경로이다, 핫키와 마찬가지이다.
        self.save_path = os.path.expanduser("~/Desktop/screenshot.png")
        # 아이콘으로 지정할 파일의 이름이다. 위와 마찬가지로 settings.json에서 불러올 예정이다.
        self.icon_path = "camera-photo.ico"
        
        # 설정을 파일에서 불러오는 과정
        self.load_settings()
        
        # 설정 창을 생성한다
        self.settings_window = SettingsWindow(self)
        
        # 시스템의 트레이 아이콘을 생성한다.
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path))
        
        # 트레이 메뉴를 만든다.
        tray_menu = QMenu()
        # 우클릭 후 Settings란에 접근 시, UI가 켜져서 원하는 세팅을 할 수 있도록 메뉴를 추가해 준다
        settings_action = tray_menu.addAction("Settings")
        # 클릭시 설정 창을 열수 있게 연결해 주는 트리거이다.
        settings_action.triggered.connect(self.show_settings)
        # 종료를 하기 위해 Exit 버튼을 추가해주는 코드이다. 마찬가지로 우클릭시 접근 가능하다
        exit_action = tray_menu.addAction("Exit")
        # 클릭 시 프로그램을 종료할 수 있게 연결해 주는 트리거이다.
        exit_action.triggered.connect(self.exit_application)
        
        # 메뉴가 트레이 아이콘에서 나올수 있게 설정하는 부분
        self.tray_icon.setContextMenu(tray_menu)
        # 트레이 아이콘을 표시한다
        self.tray_icon.show()

        # 트레이 아이콘이 없을 시 예상치 못한 오류가 발생할 수 있다.
        # 예시로 프로그램이 바로 종료되거나, 콘솔창에 아이콘이 발견되지 않았다는 오류가 뜨기도 하였다.
        # 그렇기에 settings.json에서 아이콘 파일을 불러와 트레이에서 실행되고 있는지 정상적으로 확인할 수 있게 적용한 부분이다.
        
        # 핫키를 레지스터에 적용한다.
        self.register_hotkey()

    # 세팅을 불러오는 부분
    def load_settings(self):
        # 설정 파일(settings.json)이 존재할 경우
        if os.path.exists(self.SETTINGS_FILE):
            # 존재할 경우의 시도
            try:
                # read 모드로 파일을 읽는다.
                with open(self.SETTINGS_FILE, "r") as file:
                    # json 파일이므로, json.load(file)로 불러온다
                    settings = json.load(file)
                    # 핫키를 설정하는 부분이다
                    self.hotkey = settings.get("hotkey", self.hotkey)
                    # 저장 경로를 설정하는 부분이다
                    self.save_path = settings.get("save_path", self.save_path)
                    # 아이콘을 불러오는 부분이다.
                    self.icon_path = settings.get("icon_path", self.icon_path)
            except Exception as e:
                # 오류 발생 시 경고 메시지 표시
                QMessageBox.warning(None, "Settings Error", f"Failed to load settings: {e}")

    # settings.json에 작성된 세팅을 저장한다.
    def save_settings_to_file(self):
        # 프로그램에서 지정된 핫키, 저장 경로를 settings.json에 저장하는 부분
        try:
            #settings에 저장
            settings = {
                # 핫키를 저장한다
                "hotkey": self.hotkey,
                # 저장 경로를 저장한다
                "save_path": self.save_path,
            }
            # 쓰기모드로 settings.json 파일을 연다
            with open(self.SETTINGS_FILE, "w") as file:
                # JSON파일이므로 json의 형식으로 저장한다(들여쓰기는 기본 4이므로 indent=4를 지정)
                json.dump(settings, file, indent=4)
        # 예외적 상황 발생시 오류를 인지시키기 위해 에러(경고) 메시지 표기
        except Exception as e:
            # 문제 발생시 사용자에게 보여줄 안내메시지
            QMessageBox.warning(None, "Settings Error", f"Failed to save settings: {e}")

     # 설정을 업데이트 하는 코드
    def update_settings(self, hotkey, save_path):
        # 새 핫키를 설정한다
        self.hotkey = hotkey
        # 새 저장 경로를 설정한다
        self.save_path = save_path
        
        # 핫키를 재등록한다
        self.register_hotkey()
        
        # 설정된 옵션들을 파일에 저장한다
        self.save_settings_to_file()

    # 핫키를 등록하는 부분
    def register_hotkey(self):
        # 핫키를 등록하는 방식으로 기존에 등록된 핫키를 제거한 뒤 새로운 핫키를 등록한다.
        try:
            # 기존 핫키를 제거하는 함수
            keyboard.unhook_all()
            
            # 새 핫키를 등록하는 함수
            keyboard.add_hotkey(self.hotkey, self.start_screenshot_thread)

        # 예외적인 상황으로 핫키 등록에 실패 시 표기할 메시지 
        except Exception as e:
            # 어떠한 문제가 있어서 핫키 등록에 실패했을 경우 띄워줄 메시지이다
            # ui를 불러올 수 없던 환경이거나, 고정되었을 경우 에러가 나타난 적이 있어서 추가한 부분이다
            QMessageBox.warning(None, "Error register hotkey", f"fail to register hotkey: {str(e)}")

    # 스크린샷을 찍기 위한 Thread를 시작하는 부분이다
    def start_screenshot_thread(self):
        # 1. 저장경로를 전달하여 스레드를 초기화 시킨다
        self.screenshot_thread = ScreenshotThread(self.save_path)
        # 2. 스레드에서 신호를 받을 경우 실행할 핸들러를 연결한다
        # 오류 발생시 screenshot_taken 신호를 보내며, 신호 발생 시 handle_screenshot_result가 호출된다
        self.screenshot_thread.screenshot_taken.connect(self.handle_screenshot_result)
        # 3. 스레드를 시작하며 스크린샷을 찍고 폴더에 저장하는 부분이다.
        self.screenshot_thread.start()

    # 스크린샷 이후의 결과를 나타내기 위한 코드이다
    # 만약 스크린샷이 실패했을 경우 오류를 확인할 방법이 있어야 하기 때문에, 실패했을 경우에 나타낼 에러만 구현하였다.
    def handle_screenshot_result(self, result):
        # 에러가 발생했을 경우
        if result.startswith("Error"):
            # Screenshot Eroor가 발생했다는 에러를 표기한다.
            self.tray_icon.showMessage("Screenshot Error", result, QSystemTrayIcon.Warning, 3000)

    # 설정 창 표시
    def show_settings(self):
        # UI에 현재 설정한 핫키를 표기한다
        self.settings_window.hotkey_input.setText(self.hotkey)
        # UI에 현재 지정되어 있는 저장할 경로를 표기한다
        self.settings_window.save_path_input.setText(self.save_path)
        # 창을 여는 부분이다.
        self.settings_window.show()
        # 실행시 잘 켜졌는지 볼 수 있게 창을 최상단으로 끌어올리는 부분이다.
        self.settings_window.raise_()

    # 애플리케이션의 종료를 확인하는 부분이다
    def exit_application(self):

        # 트레이 아이콘에서 우클릭 후 Exit 클릭시 받는 응답이다
        reply = QMessageBox.question(
            # 팝업창 제목은 Exit, 내용은 정말로 SCOP를 종료할 것인지 묻는다
            None, "Exit", "Really Exit SCOP?", 
            # 팝업창 버튼에는 YES와 NO가 생성되게 한다
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        # 만약 YES를 클릭할 경우, 프로그램을 종료하게 한다, 프로그램이 종료되는 경우는 Exit로만 종료할 수 있게 한다
        if reply == QMessageBox.Yes:
            self.app.quit()

# 프로그램의 메인 함수
def main():
    # PyQt5 패키지의 애플리케이션 초기화
    app = QApplication(sys.argv)
    # 스크린샷 애플리케이션의 인스턴스를 생성한다
    screenshot_app = ScreenshotApp(app)
    # 프로그램 종료 시 세팅을 저장하도록 한다
    app.aboutToQuit.connect(screenshot_app.save_settings_to_file)
    # 기본적으로 프로그램이 백그라운드에서 계속 동작하면서 사용하게 하고 싶기 때문에, 프로그램이 무한 루프를 돌게 한다
    sys.exit(app.exec_())

# 애플리케이션의 종료를 확인하는 부분인 exit_application에 도달하여 Exit -> Yes가 이루어질 경우에는 무한 루프를 나와 프로그램을 종료한다

# 프로그램의 실행 시작점을 의미, GUI 실행이 포함되어 있다.
if __name__ == "__main__":
    main()
