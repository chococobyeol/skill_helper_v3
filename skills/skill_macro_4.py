import time
import win32api
import win32con
import keyboard

class SkillMacro4Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        self.use_party_skill = False  # 파티 스킬 사용 여부 설정
        
        # 키 설정
        self.ESC_KEY = win32con.VK_ESCAPE
        self.Z_KEY = ord('Z')  # Z키
        self.Q_KEY = ord('Q')  # Q키
        self.W_KEY = ord('W')  # W키
        self.P_KEY = ord('P')  # P키
        self.HOME_KEY = win32con.VK_HOME  # Home키
        self.ENTER_KEY = win32con.VK_RETURN  # Enter키
        self.TAB_KEY = win32con.VK_TAB  # Tab키
        self.SHIFT_KEY = win32con.VK_SHIFT  # Shift키
        self.TOGGLE_KEY = 'F4'
        
        # 파티 기능 토글 단축키 설정 수정
        keyboard.add_hotkey('alt+p', self.toggle_party_skill)

    def toggle_party_skill(self):
        self.use_party_skill = not self.use_party_skill
        status = "활성화" if self.use_party_skill else "비활성화"
        print(f"\nF4 파티 기능 {status}")

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)

    def send_shift_key(self, key):
        # Shift 누르기
        win32api.keybd_event(self.SHIFT_KEY, 0, 0, 0)
        time.sleep(0.025)
        # 문자 누르기
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.025)
        # 문자 떼기
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.025)
        # Shift 떼기
        win32api.keybd_event(self.SHIFT_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.025)

    def use_skill(self):
        print("스킬 매크로 4 사용")
        
        # ESC
        self.send_key(self.ESC_KEY)
        time.sleep(0.1)

        # 키 블록
        keyboard.block_key('up')
        keyboard.block_key('down')
        keyboard.block_key('left')
        keyboard.block_key('right')
        keyboard.block_key('enter')
        
        # Z(쉬프트+z)
        self.send_shift_key(self.Z_KEY)
        time.sleep(0.1)

        # Q
        self.send_key(self.Q_KEY)
        time.sleep(0.1)
        
        # HOME > ENTER
        self.send_key(self.HOME_KEY)
        time.sleep(0.1)
        self.send_key(self.ENTER_KEY)
        time.sleep(0.1)
        
        # Z
        self.send_shift_key(self.Z_KEY)
        time.sleep(0.1)
        
        # W > ENTER
        self.send_key(self.W_KEY)
        time.sleep(0.1)
        self.send_key(self.ENTER_KEY)
        time.sleep(0.1)

        # 파티 스킬 부분 - use_party_skill이 True일 때만 실행
        if self.use_party_skill:
            # TAB > TAB
            self.send_key(self.TAB_KEY)
            time.sleep(0.1)
            self.send_key(self.TAB_KEY)
            time.sleep(0.1)
            
            # Z
            self.send_shift_key(self.Z_KEY)
            time.sleep(0.1)
            
            # Q
            self.send_key(self.Q_KEY)
            time.sleep(0.1)
            
            # Z
            self.send_shift_key(self.Z_KEY)
            time.sleep(0.1)
            
            # W
            self.send_key(self.W_KEY)
            time.sleep(0.1)    

        self.send_key(self.ESC_KEY)
        time.sleep(0.025)
        # 키 언블록
        keyboard.unblock_key('up')
        keyboard.unblock_key('down')
        keyboard.unblock_key('left')
        keyboard.unblock_key('right')
        keyboard.unblock_key('enter')
        time.sleep(0.1)
        
        # 한 번 실행 후 자동으로 비활성화
        self.is_running = False