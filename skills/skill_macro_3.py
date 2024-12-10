import time
import win32api
import win32con
import keyboard

class SkillMacro3Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        
        # 키 설정
        self.SKILL_KEY = 0x35  # 5키
        self.ESC_KEY = win32con.VK_ESCAPE
        self.TAB_KEY = win32con.VK_TAB
        self.TOGGLE_KEY = 'F3'

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)

    def use_skill(self):
        print("스킬 매크로 3 사용")
        
        # 키 블록을 가장 먼저 적용
        keyboard.block_key('up')
        keyboard.block_key('down')
        keyboard.block_key('left')
        keyboard.block_key('right')
        keyboard.block_key('enter')
        
        try:
            self.send_key(self.ESC_KEY)  # ESC
            time.sleep(0.01)
            
            self.send_key(self.TAB_KEY)  # TAB
            time.sleep(0.1)
            self.send_key(self.TAB_KEY)  # TAB
            time.sleep(0.1)

            # 5키 4번 입력
            for _ in range(4):
                self.send_key(self.SKILL_KEY)  # 5
                time.sleep(0.025)

            self.send_key(self.ESC_KEY)  # ESC
            time.sleep(0.01)

        finally:
            # 키 언블록은 finally에서 보장
            keyboard.unblock_key('up')
            keyboard.unblock_key('down')
            keyboard.unblock_key('left')
            keyboard.unblock_key('right')
            keyboard.unblock_key('enter')
            
            # 이동용 딜레이
            time.sleep(0.3)
