import time
import win32api
import win32con
import keyboard

class SkillMacro9Controller:
    def __init__(self):
        self.is_running = False
        self.macro_controller = None
        self.has_init_sequence = False
        self.ESC_KEY = win32con.VK_ESCAPE
        self.TAB_KEY = 0x09
        self.NUM_6_KEY = 0x36
        self.prev_healing_recovering = False
        self.was_running = False

        self.key_delay = 0.1
        self.skill_delay = 0.5

    def send_key(self, key, delay=None):
        if delay is None:
            delay = self.key_delay
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(delay)

    def is_healing_or_recovering(self):
        if self.macro_controller and self.macro_controller.heal_controller:
            return (self.macro_controller.heal_controller.is_healing or
                    self.macro_controller.heal_controller.mana_controller.is_recovering)
        return False

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
        if not self.is_running and not self.was_running:
            return

        curr_healing_recovering = self.is_healing_or_recovering()

        if self.is_running and not self.was_running:
            self.has_init_sequence = False
            print("[DEBUG] 스킬9 시작: 초기화 필요")
        elif not self.is_running and self.was_running:
            self.has_init_sequence = False
            print("[DEBUG] 스킬9 정지: esc")
            if self.macro_controller:
                with self.macro_controller.key_input_lock:
                    self.send_key(self.ESC_KEY)
            self.prev_healing_recovering = False
            self.was_running = self.is_running
            return

        if not self.is_running:
            if self.macro_controller:
                with self.macro_controller.key_input_lock:
                    self.send_key(self.ESC_KEY)
            self.has_init_sequence = False
            self.prev_healing_recovering = False
            self.was_running = self.is_running
            return

        if curr_healing_recovering:
            if not self.prev_healing_recovering:
                print("[DEBUG] 힐/마나 회복: 스킬 대기")
            self.prev_healing_recovering = True
        else:
            if self.prev_healing_recovering:
                print("[DEBUG] 힐/마나 회복 종료: 다음 턴 초기화")
                self.has_init_sequence = False
                self.prev_healing_recovering = False

        if self.macro_controller:
            with self.macro_controller.key_input_lock:
                if not self.has_init_sequence:
                    print("[DEBUG] 초기 시퀀스: esc > tab > tab")
                    self.block_keys()
                    try:
                        self.send_key(self.ESC_KEY)
                        self.send_key(self.TAB_KEY)
                        self.send_key(self.TAB_KEY)
                    finally:
                        self.unblock_keys()
                    self.has_init_sequence = True

                if not curr_healing_recovering:
                    print("[DEBUG] 6키 사용")
                    self.send_key(self.NUM_6_KEY, delay=self.skill_delay)
        else:
            if not self.has_init_sequence:
                print("[DEBUG] 초기 시퀀스(컨트롤러 없음): esc > tab > tab")
                self.send_key(self.ESC_KEY)
                self.send_key(self.TAB_KEY)
                self.send_key(self.TAB_KEY)
                self.has_init_sequence = True
            if not curr_healing_recovering:
                print("[DEBUG] 6키 사용(컨트롤러 없음)")
                self.send_key(self.NUM_6_KEY, delay=self.skill_delay)

        self.was_running = self.is_running 