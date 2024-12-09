import time
import win32api
import win32con
import keyboard

class SkillMacro1Controller:  # 클래스 이름도 변경
    def __init__(self):
        self.is_active = True
        self.is_running = False
        self.skill_area = None  # 스킬 감지 영역 추가
        
        # 키 설정
        self.SKILL_KEY = 0x36  # 6키
        self.ESC_KEY = win32con.VK_ESCAPE
        self.TAB_KEY = win32con.VK_TAB
        self.TOGGLE_KEY = 'F1'

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)

    def use_skill(self):
        print("스킬 매크로 1 사용")
        
        self.send_key(self.ESC_KEY)  # ESC
        # 키 블록
        keyboard.block_key('up')
        keyboard.block_key('down')
        keyboard.block_key('left')
        keyboard.block_key('right')
        keyboard.block_key('enter')  
        
        time.sleep(0.025)
        self.send_key(self.TAB_KEY)  # TAB
        time.sleep(0.05)
        self.send_key(self.TAB_KEY)  # TAB
        time.sleep(0.025)
        self.send_key(self.SKILL_KEY)  # 6
        time.sleep(0.025)
        self.send_key(self.ESC_KEY)  # ESC
                # 방향키 unblock
        keyboard.unblock_key('up')
        keyboard.unblock_key('down')
        keyboard.unblock_key('left')
        keyboard.unblock_key('right')
        keyboard.unblock_key('enter')
        time.sleep(0.2)


