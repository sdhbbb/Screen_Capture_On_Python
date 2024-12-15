# Screen_Capture_On_Python, SCOP
Open Source Capture Program Project
 <br />오픈 소스 캡쳐 프로그램 프로젝트, SCOP 입니다
 
Capture screen using python.
 <br />파이썬을 이용한 스크린 캡쳐 도구입니다.

Built for Windows 11, feel free to use it in your own context.
 <br />윈도우 11 환경에서 제작되었으며, 상황에 맞게 자유롭게 사용하거나 수정하실 수 있습니다.

Use PyQt5 for gui pyautogui package, some environment can't work.
 <br />gui 이용을 위한 PyQt 패키지 혹은 pyautogui 이용으로 일부 환경에서는 정상적인 기능이 작동하지 않을수도 있습니다.

***




# how to running it?
Use sys, os, keyboard, json, PyQt5, pyautogui, etc
 <br />If you don't have that package, use pip command to download the module

For PyQt5, write code to specify the location of the plugin folder, because some environment(ex, windows 11) may not recognize the location of the plugin
 <br />If it works fine without specifying the location, you can comment out the code above and move on.

sys, os, keyboard, json, PyQt5, pyautogui 등의 패키지를 이용하였습니다.
 <br />만약 해당하는 패키지를 가지고 있지 않다면, pip 커맨드를 통해 해당 모듈을 다운받아주세요.

 ```python
ex) pip install json keyboard pyautogui PyQt5
```

PyQt5의 경우, 일부 환경에서는 플러그인의 위치를 인식하지 못하는 경우로 인하여 플러그인 폴더의 위치를 명시하는 코드를 작성하였습니다.
 <br />만일 위치를 명시하지 않아도 작동이 올바르게 되는 경우, 위 코드는 주석 처리 후 넘어가도 됩니다.

example)
 <br />SCOP can't specifying the location, use this code. If, it works fine, don't use it.
 <br />오류로 인해 QT 플러그인의 경로를 명시적으로 적어둔 코드 작성, 오류가 없을 시 사용하지 않아도 됨.
 <br />qt_plugin_path = r"C:\Users\Username(ex.Hong-Gildong)\AppData\Local\Programs\Python\Python313\Lib\site-packages\PyQt5\Qt5\plugins"
 <br />os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

In most cases, it will be installed in the Lib/site-packages folder of your Python installation folder, but if you have installed it elsewhere, please specify the location of your own installation.
 <br />대부분의 경우, 파이썬 설치 폴더의 Lib\site-packages 폴더 안에 설치되나, 다른 곳에 설치하였을 경우, 직접 설치된 위치를 지정하여 주시면 됩니다.
***





# future plan
+ add specifying zone capture function
+ add support various extensions
+ etc...

+ 영역 캡쳐 기능 추가
+ 다양한 확장자 지원
+ 기타 등등

