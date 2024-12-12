# skills/skill_macro_2.py
import time
import win32api
import win32con
import keyboard

class SkillMacro2Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        
        # 키 설정
        self.ESC_KEY = win32con.VK_ESCAPE  # ESC키
        self.SKILL_KEY = 0x39  # 9키
        self.UP_KEY = win32con.VK_UP  # 위 방향키
        self.ENTER_KEY = win32con.VK_RETURN  # 엔터키
        self.TOGGLE_KEY = 'F2'

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.005)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.005)

    def use_skill(self):
        print("스킬 매크로 2 사용")
        
        # 첫 번째 9>위>엔터
        self.send_key(self.ESC_KEY)  # ESC  
        time.sleep(0.03)
        self.send_key(self.SKILL_KEY)  # 9
        time.sleep(0.03)
        self.send_key(self.UP_KEY)     # 위
        time.sleep(0.03)
        self.send_key(self.ENTER_KEY)  # 엔터
        time.sleep(0.03)