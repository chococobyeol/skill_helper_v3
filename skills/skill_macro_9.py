import time
import win32api
import win32con
import keyboard
import pyautogui
import os
import numpy as np
import cv2
from threading import Thread
from random_delay import add_delay

class SkillMacro9Controller:
    def __init__(self):
        self.is_running = False
        self.macro_controller = None
        self.has_init_sequence = False
        self.ESC_KEY = win32con.VK_ESCAPE
        self.TAB_KEY = 0x09
        self.NUM_6_KEY = 0x36
        self.UP_KEY = win32con.VK_UP
        self.prev_healing_recovering = False
        self.was_running = False
        
        # 기본 감지 영역 설정 (파란색 영역으로 수정)
        self.skill_area = (1150, 773, 440, 75)  # x, y, width, height

        self.key_delay = 0.05
        self.skill_delay = 0.5

        # 이미지 파일 경로 설정
        self.img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
        self.kill_mob_path = os.path.join(self.img_dir, 'kill_mob.png')
        self.kill_mob2_path = os.path.join(self.img_dir, 'kill_mob2.png')
        self.detect_atk_path = os.path.join(self.img_dir, 'detect_atk.png')
        
        self.check_image_files()

        self.detected_kill_mob = False  # 이미지 감지 결과 저장
        self.detected_attack = True     # 공격 감지 결과 저장
        self.image_check_thread = None  # 이미지 감지 스레드
        
    def check_image_files(self):
        files = [self.kill_mob_path, self.kill_mob2_path, self.detect_atk_path]
        missing_files = []
        for file in files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print("\n=== 이미지 파일 확인 필요 ===")
            print("다음 파일들이 없습니다:")
            for file in missing_files:
                print(f"- {file}")
            print("=========================\n")

    def find_image(self, image_path):
        try:
            if self.skill_area is None:
                print("[DEBUG] 스킬 영역이 설정되지 않음")
                return False
            
            print(f"[DEBUG] 이미지 매칭 시도: {os.path.basename(image_path)}")
            print(f"[DEBUG] 감지 영역: {self.skill_area}")
            
            # QRect를 튜플로 변환
            if isinstance(self.skill_area, tuple):
                region = self.skill_area
            else:
                region = (
                    self.skill_area.x(),
                    self.skill_area.y(),
                    self.skill_area.width(),
                    self.skill_area.height()
                )
            
            print(f"[DEBUG] 스크린샷 영역: {region}")
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            
            template = cv2.imread(image_path)
            if template is None:
                print(f"[DEBUG] 템플릿 이미지 로드 실패: {image_path}")
                return False
            
            print(f"[DEBUG] 스크린샷 크기: {screen_bgr.shape}")
            print(f"[DEBUG] 템플릿 크기: {template.shape}")
            
            result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"[DEBUG] 이미지 매칭 점수: {max_val:.2f}")
            
            if max_val >= 0.9:
                print(f"[DEBUG] 이미지 매칭 성공! (점수: {max_val:.2f})")
                return True
            
            print("[DEBUG] 이미지 매칭 실패")
            return False
            
        except Exception as e:
            print(f"[DEBUG] 이미지 감지 오류: {str(e)}")
            print(f"[DEBUG] 에러 발생 위치: {e.__traceback__.tb_lineno}")
            return False

    def check_kill_mob_image(self):
        print("[DEBUG] 킬몹 이미지 체크 시작")
        # 두 이미지 중 하나라도 감지되면 True 반환
        result = self.find_image(self.kill_mob_path) or self.find_image(self.kill_mob2_path)
        print(f"[DEBUG] 킬몹 이미지 체크 결과: {result}")
        return result

    def check_detect_atk(self):
        print("[DEBUG] 공격 감지 이미지 체크")
        result = self.find_image(self.detect_atk_path)
        print(f"[DEBUG] 공격 감지 결과: {result}")
        return result

    def send_key(self, key, delay=None):
        if delay is None:
            delay = self.key_delay
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(add_delay(0.02))
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(add_delay(delay))

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

    def start_image_check(self):
        if self.image_check_thread is None or not self.image_check_thread.is_alive():
            self.image_check_thread = Thread(target=self.image_check_loop)
            self.image_check_thread.daemon = True
            self.image_check_thread.start()

    def image_check_loop(self):
        while self.is_running:
            if not self.is_healing_or_recovering():
                self.detected_kill_mob = self.check_kill_mob_image()
                self.detected_attack = self.check_detect_atk()
            time.sleep(0.1)  # 이미지 체크 간격

    def use_skill(self):
        if not self.is_running and not self.was_running:
            return

        curr_healing_recovering = self.is_healing_or_recovering()

        if self.is_running and not self.was_running:
            self.has_init_sequence = False
            print("[DEBUG] 스킬9 시작: 초기화 필요")
            print(f"[DEBUG] skill_area 설정 상태: {self.skill_area}")
            self.start_image_check()  # 이미지 감지 스레드 시작
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
            return  # 힐링/마나 회복 중일 때는 여기서 리턴

        if self.prev_healing_recovering:
            print("[DEBUG] 힐/마나 회복 종료: 다음 턴 초기화")
            self.has_init_sequence = False
            self.prev_healing_recovering = False

        if not self.has_init_sequence:
            print("[DEBUG] 초기 시퀀스: esc > tab > tab")
            if self.macro_controller:
                with self.macro_controller.key_input_lock:
                    self.block_keys()
                    try:
                        self.send_key(self.ESC_KEY)
                        self.send_key(self.TAB_KEY)
                        self.send_key(self.TAB_KEY)
                    finally:
                        self.unblock_keys()
            self.has_init_sequence = True

        # 스킬 사용
        if self.macro_controller:
            with self.macro_controller.key_input_lock:
                print("[DEBUG] 6키 사용")
                self.send_key(self.NUM_6_KEY, delay=self.skill_delay)
                
                print("[DEBUG] 이미지 체크 시작")
                kill_mob_detected = self.check_kill_mob_image()
                print(f"[DEBUG] 킬몹 감지 결과: {kill_mob_detected}")
                
                attack_detected = self.check_detect_atk()
                print(f"[DEBUG] 공격 감지 결과: {attack_detected}")
                
                # 킬몹 이미지 감지 또는 공격 감지 이미지가 없을 경우 추가 동작
                if kill_mob_detected or not attack_detected:
                    print("[DEBUG] 추가 키 입력 시작")
                    time.sleep(0.1)
                    self.send_key(self.ESC_KEY)
                    time.sleep(0.1)
                    self.send_key(self.TAB_KEY)
                    time.sleep(0.1)
                    print("[DEBUG] 킬몹 감지 또는 공격 미감지: 윗방향키 > 탭")
                    self.send_key(self.UP_KEY)
                    time.sleep(0.1)
                    self.send_key(self.TAB_KEY)
                    print("[DEBUG] 추가 키 입력 완료")
                else:
                    print("[DEBUG] 추가 키 입력 불필요")

        self.was_running = self.is_running