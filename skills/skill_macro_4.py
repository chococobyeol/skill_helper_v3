# skill_macro_4.py
import time
import win32api
import win32con
import keyboard

class SkillMacro4Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        self.use_party_skill = False  # 파티 스킬 사용 여부
        
        self.ESC_KEY = win32con.VK_ESCAPE
        self.Z_KEY = ord('Z')
        self.Q_KEY = ord('Q')
        self.W_KEY = ord('W')
        self.P_KEY = ord('P')
        self.HOME_KEY = win32con.VK_HOME
        self.ENTER_KEY = win32con.VK_RETURN
        self.TAB_KEY = win32con.VK_TAB
        self.SHIFT_KEY = win32con.VK_SHIFT
        self.TOGGLE_KEY = 'F4'

        self.macro_controller = None  # MacroController 할당 필요
        keyboard.add_hotkey('alt+p', self.toggle_party_skill)

        self.key_delay = 0.01  # 키 입력 딜레이 최소화

    def toggle_party_skill(self):
        self.use_party_skill = not self.use_party_skill
        status = "활성화" if self.use_party_skill else "비활성화"
        print(f"\nF4 파티 기능 {status}")

    def send_key(self, key, delay=None):
        if delay is None:
            delay = self.key_delay
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(delay)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(delay)

    def send_shift_key(self, key):
        # Shift + 키 입력
        try:
            win32api.keybd_event(self.SHIFT_KEY, 0, 0, 0)
            time.sleep(0.05)  # shift 키를 누르고 약간의 대기
            win32api.keybd_event(key, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(self.SHIFT_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
        except Exception as e:
            print(f"[DEBUG] Shift+{chr(key)} 입력 실패: {e}")

    def block_keys(self):
        # 방향키, 엔터키 블록
        for k in ['up', 'down', 'left', 'right', 'enter']:
            try:
                keyboard.block_key(k)
            except Exception as e:
                print(f"키 블록 오류({k}): {e}")

    def unblock_keys(self):
        for k in ['up', 'down', 'left', 'right', 'enter']:
            try:
                keyboard.unblock_key(k)
            except Exception as e:
                print(f"키 언블록 오류({k}): {e}")

    def is_healing_or_recovering(self):
        # 힐/마나 회복 상태 확인
        if self.macro_controller and self.macro_controller.heal_controller:
            return (self.macro_controller.heal_controller.is_healing or
                    self.macro_controller.heal_controller.mana_controller.is_recovering)
        return False

    def use_skill(self):
        print("스킬 매크로 4 사용")
        
        if self.macro_controller:
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
                    # ESC
                    print("[DEBUG] F4: ESC 키 입력")
                    self.send_key(self.ESC_KEY)
                    time.sleep(0.05)

                    # Z(Shift+Z)
                    print("[DEBUG] F4: Shift+Z 키 입력")
                    self.send_shift_key(self.Z_KEY)
                    time.sleep(0.05)

                    # Q
                    print("[DEBUG] F4: Q 키 입력")
                    self.send_key(self.Q_KEY)
                    time.sleep(0.05)

                    # HOME > ENTER
                    print("[DEBUG] F4: HOME > ENTER 키 입력")
                    self.send_key(self.HOME_KEY)
                    time.sleep(0.05)
                    self.send_key(self.ENTER_KEY)
                    time.sleep(0.05)

                    # Z
                    print("[DEBUG] F4: Shift+Z 키 입력 (2)")
                    self.send_shift_key(self.Z_KEY)
                    time.sleep(0.05)

                    # W > ENTER
                    print("[DEBUG] F4: W > ENTER 키 입력")
                    self.send_key(self.W_KEY)
                    time.sleep(0.05)
                    self.send_key(self.ENTER_KEY)
                    time.sleep(0.05) 

                    # ESC
                    print("[DEBUG] F4: ESC 키 입력 (2)")
                    self.send_key(self.ESC_KEY)
                    time.sleep(0.05)

                    if self.use_party_skill:
                        # TAB > TAB
                        print("[DEBUG] F4: TAB > TAB 키 력")
                        self.send_key(self.TAB_KEY)
                        time.sleep(0.05)
                        self.send_key(self.TAB_KEY)
                        time.sleep(0.05)
                        
                        # Z
                        print("[DEBUG] F4: Shift+Z 키 입력 (3)")
                        self.send_shift_key(self.Z_KEY)
                        time.sleep(0.05)
                        
                        # Q
                        print("[DEBUG] F4: Q 키 입력 (2)")
                        self.send_key(self.Q_KEY)
                        time.sleep(0.05)
                        
                        # Z
                        print("[DEBUG] F4: Shift+Z 키 입력 (4)")
                        self.send_shift_key(self.Z_KEY)
                        time.sleep(0.05)
                        
                        # W
                        print("[DEBUG] F4: W 키 입력 (2)")
                        self.send_key(self.W_KEY)
                        time.sleep(0.05)

                    self.send_key(self.ESC_KEY)
                    time.sleep(0.05)
                finally:
                    self.unblock_keys()
                    # 힐링/마나 컨트롤러 상태 복원
                    if self.macro_controller.heal_controller:
                        self.macro_controller.heal_controller.is_running = heal_was_running
                        self.macro_controller.heal_controller.mana_controller.is_running = mana_was_running

        print("스킬 매크로 4 실행 완료")