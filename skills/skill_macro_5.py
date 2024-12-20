import time
import win32api
import win32con
import keyboard
from random_delay import add_delay

class SkillMacro5Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        self.macro_controller = None
        
        # 키 설정
        self.ESC_KEY = win32con.VK_ESCAPE
        self.Z_KEY = ord('Z')
        self.A_KEY = ord('A')
        self.V_KEY = ord('V')
        self.ENTER_KEY = win32con.VK_RETURN
        self.SHIFT_KEY = win32con.VK_SHIFT
        self.CTRL_KEY = win32con.VK_CONTROL
        self.TOGGLE_KEY = 'alt+f1'

        self.key_delay = 0.01

    def send_key(self, key, delay=None):
        if delay is None:
            delay = self.key_delay
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(add_delay(delay))
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(add_delay(delay))

    def send_shift_key(self, key):
        try:
            win32api.keybd_event(self.SHIFT_KEY, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(self.SHIFT_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
        except Exception as e:
            print(f"[DEBUG] Shift+{chr(key)} 입력 실패: {e}")

    def send_ctrl_key(self, key):
        try:
            win32api.keybd_event(self.CTRL_KEY, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(self.CTRL_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
        except Exception as e:
            print(f"[DEBUG] Ctrl+{chr(key)} 입력 실패: {e}")

    def block_keys(self):
        try:
            keyboard.block_key('up')
            keyboard.block_key('down')
            keyboard.block_key('left')
            keyboard.block_key('right')
            keyboard.block_key('enter')
        except Exception as e:
            print("키 블록 오류:", e)

    def unblock_keys(self):
        try:
            keyboard.unblock_key('up')
            keyboard.unblock_key('down')
            keyboard.unblock_key('left')
            keyboard.unblock_key('right')
            keyboard.unblock_key('enter')
        except Exception as e:
            print("키 언블록 오류:", e)

    def use_skill(self):
        print("스킬 매크로 5 사용")
        
        if self.macro_controller:
            # alt 키가 떼질 때까지 대기
            while keyboard.is_pressed('alt'):
                time.sleep(0.01)
            time.sleep(0.05)  # 추가 안전 대기
            
            # 힐링/마나 컨트롤러 상태 저장
            heal_was_running = False
            mana_was_running = False
            if self.macro_controller.heal_controller:
                heal_was_running = self.macro_controller.heal_controller.is_running
                mana_was_running = self.macro_controller.heal_controller.mana_controller.is_running
                # 힐링/마나 회복 일시 중지
                self.macro_controller.heal_controller.is_running = False
                self.macro_controller.heal_controller.mana_controller.is_running = False

            with self.macro_controller.key_input_lock:
                self.block_keys()
                try:
                    # Shift+Z
                    print("[DEBUG] 매크로5: Shift+Z 키 입력")
                    self.send_shift_key(self.Z_KEY)
                    time.sleep(0.03)

                    # Shift+A
                    print("[DEBUG] 매크로5: Shift+A 키 입력")
                    self.send_shift_key(self.A_KEY)
                    time.sleep(0.03)

                    # Ctrl+V
                    print("[DEBUG] 매크로5: Ctrl+V 키 입력")
                    self.send_ctrl_key(self.V_KEY)
                    time.sleep(0.03)

                    # ENTER
                    print("[DEBUG] 매크로5: ENTER 키 입력")
                    self.send_key(self.ENTER_KEY)
                    time.sleep(0.03)

                finally:
                    self.unblock_keys()
                    # 힐링/마나 컨트롤러 상태 복원
                    if self.macro_controller.heal_controller:
                        self.macro_controller.heal_controller.is_running = heal_was_running
                        self.macro_controller.heal_controller.mana_controller.is_running = mana_was_running

        print("스킬 매크로 5 실행 완료")