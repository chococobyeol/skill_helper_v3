import time
import win32api
import win32con
import keyboard
import pyautogui
import os
import numpy as np
import cv2

class SkillMacro9Controller:
    def __init__(self):
        self.is_active = True
        self.is_running = False
        self.fail_count = 0
        self.MAX_FAILS = 10  # 최대 실패 횟수
        self.MAX_KILL_ATTEMPTS = 100  # 킬 시도 최대 횟수
        self.macro_controller = None  # 매크로 컨트롤러 참조
        self.skill_area = None  # 스킬 감지 영역
        
        # 키 설정
        self.SKILL_KEY = 0x36  # 6키
        self.ENTER_KEY = win32con.VK_RETURN
        self.UP_KEY = win32con.VK_UP
        self.TOGGLE_KEY = 'F9'
        
        # 이미지 파일 경로 설정
        self.img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
        self.detect_atk_path = os.path.join(self.img_dir, 'detect_atk.png')
        self.kill_mob_path = os.path.join(self.img_dir, 'kill_mob.png')
        
        self.check_image_files()

    def check_image_files(self):
        files = [self.detect_atk_path, self.kill_mob_path]
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

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)

    def find_image(self, image_path):
        try:
            if self.skill_area is None:  # 영역이 설정되지 않은 경우 기본 영역 사용
                region = (1150, 678, 450, 182)
            else:
                region = (self.skill_area.x(), self.skill_area.y(), 
                         self.skill_area.width(), self.skill_area.height())
            
            # pyautogui 대신 OpenCV 직접 사용
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
            
            template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"템플릿 이미지를 불러올 수 없습니다: {image_path}")
                return False
            
            # 템플릿 매칭 수행
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 임계값을 0.9로 조정 (90% 이상 일치)
            if max_val >= 0.9:
                location = (max_loc[0], max_loc[1], template.shape[1], template.shape[0])
                print(f"이미지 발견: {os.path.basename(image_path)} 위치: {location}")
                return True
            return False
            
        except Exception as e:
            if not isinstance(e, pyautogui.ImageNotFoundException):
                print(f"이미지 검색 중 오류: {str(e)}")
            return False

    def try_once(self):
        try:
            # 첫 번째 시도: 6 > 방향키 > 엔터
            self.send_key(self.SKILL_KEY)  # 6
            time.sleep(0.025)
            self.send_key(self.UP_KEY)     # 방향키
            time.sleep(0.025)
            self.send_key(self.ENTER_KEY)  # 엔터
            time.sleep(0.05)  # 스킬 사용 대기

            # 즉사 체크
            if self.find_image(self.kill_mob_path):
                print("몹 처치 성공")
                self.fail_count = 0
                return True

            # 스킬 실행 감지
            if not self.find_image(self.detect_atk_path):
                print("스킬 실행 감지 실패")
                self.fail_count += 1
                return False

            print("스킬 실행 감지 - 킬 시도")
            self.fail_count = 0  # 스킬 실행 성공시 실패 카운트 리셋
            
            # 스킬 실행 감지됐을 때는 6>엔터만 반복
            kill_attempts = 0
            while kill_attempts < self.MAX_KILL_ATTEMPTS and self.is_running:
                # 힐/마나 체크
                if (self.macro_controller.heal_controller.is_healing or 
                    self.macro_controller.heal_controller.mana_controller.is_recovering):
                    print("힐/마나 회복을 위해 킬 시도 중단")
                    return True

                self.send_key(self.SKILL_KEY)  # 6
                time.sleep(0.025)
                self.send_key(self.ENTER_KEY)  # 엔터
                time.sleep(0.05)

                if self.find_image(self.kill_mob_path):  # 몹 킬 감지
                    print("몹 처치 성공")
                    self.fail_count = 0
                    return True

                kill_attempts += 1
                if kill_attempts % 10 == 0:
                    print(f"킬 시도 {kill_attempts}/{self.MAX_KILL_ATTEMPTS}")

            print(f"{self.MAX_KILL_ATTEMPTS}회 시도 후에도 처치 실패")
            return False

        except Exception as e:
            print(f"킬러 매크로 오류: {str(e)}")
            self.fail_count += 1
            return False
        